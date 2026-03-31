#include "app_runtime.h"

#include <stdbool.h>
#include <stdio.h>

#include "FreeRTOS.h"
#include "queue.h"
#include "semphr.h"
#include "task.h"
#include "hub_state.h"
#include "hardware/gpio.h"
#include "hardware/watchdog.h"
#include "pico/stdlib.h"
#include "ring_buffer.h"
#include "sensor_hub.h"
#include "sensor_source.h"
#include "telemetry.h"

typedef struct {
    QueueHandle_t sample_queue;
    SemaphoreHandle_t ring_mutex;
    sample_ring_buffer_t ring;
} app_context_t;

static app_context_t g_app;

static uint32_t millis_since_boot(void) {
    return to_ms_since_boot(get_absolute_time());
}

static TickType_t sample_period_ticks(void) {
    uint32_t period_ms = 1000u / (SENSOR_HUB_SAMPLE_RATE_HZ == 0 ? 1u : SENSOR_HUB_SAMPLE_RATE_HZ);
    if (period_ms == 0u) {
        period_ms = 1u;
    }
    return pdMS_TO_TICKS(period_ms);
}

static void store_sample(const sensor_sample_t *sample) {
    if (xSemaphoreTake(g_app.ring_mutex, portMAX_DELAY) == pdTRUE) {
        ring_buffer_push(&g_app.ring, sample);
        xSemaphoreGive(g_app.ring_mutex);
    }
}

static bool fetch_latest_sample(sensor_sample_t *sample_out, size_t *ring_count_out) {
    bool found = false;

    if (xSemaphoreTake(g_app.ring_mutex, portMAX_DELAY) == pdTRUE) {
        found = ring_buffer_latest(&g_app.ring, sample_out);
        if (ring_count_out != NULL) {
            *ring_count_out = ring_buffer_count(&g_app.ring);
        }
        xSemaphoreGive(g_app.ring_mutex);
    }

    return found;
}

static void sensor_task(void *unused) {
    TickType_t last_wake = xTaskGetTickCount();
    (void)unused;

    for (;;) {
        sensor_sample_t sample;
        bool ok = sensor_source_read(&sample, millis_since_boot());
        if (!ok) {
            hub_state_increment_sensor_failure();
            hub_state_set_fault_flags(SENSOR_HUB_FAULT_SENSOR_FAILURE);
        } else {
            store_sample(&sample);
            if (xQueueSend(g_app.sample_queue, &sample, 0) != pdPASS) {
                hub_state_increment_queue_overflow();
            }
        }

        hub_state_note_sensor_heartbeat();
        vTaskDelayUntil(&last_wake, sample_period_ticks());
    }
}

static void telemetry_task(void *unused) {
    TickType_t last_wake = xTaskGetTickCount();
    sensor_sample_t last_sample = {0};
    bool have_sample = false;
    (void)unused;

    for (;;) {
        sensor_sample_t queued_sample;
        size_t ring_count = 0u;

        while (xQueueReceive(g_app.sample_queue, &queued_sample, 0) == pdPASS) {
            last_sample = queued_sample;
            have_sample = true;
        }

        if (!have_sample) {
            have_sample = fetch_latest_sample(&last_sample, &ring_count);
        } else {
            sensor_sample_t latest_sample;
            if (fetch_latest_sample(&latest_sample, &ring_count)) {
                last_sample = latest_sample;
            } else {
                ring_count = 0u;
            }
        }

        if (have_sample) {
            char line[512];
            hub_status_t status = hub_state_snapshot();
            size_t queue_depth = (size_t)uxQueueMessagesWaiting(g_app.sample_queue);
            int written = telemetry_format_json(
                line,
                sizeof(line),
                &last_sample,
                &status,
                ring_count,
                queue_depth
            );
            if (written > 0) {
                if (printf("%s", line) < 0) {
                    hub_state_increment_serial_disconnect();
                }
                fflush(stdout);
            }
        }

        hub_state_note_telemetry_heartbeat();
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(SENSOR_HUB_TELEMETRY_INTERVAL_MS));
    }
}

static void heartbeat_task(void *unused) {
    bool led_state = false;
    (void)unused;

#ifdef PICO_DEFAULT_LED_PIN
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
#endif

    for (;;) {
#ifdef PICO_DEFAULT_LED_PIN
        gpio_put(PICO_DEFAULT_LED_PIN, led_state);
#endif
        led_state = !led_state;
        hub_state_note_blink_heartbeat();
        vTaskDelay(pdMS_TO_TICKS(250));
    }
}

static uint32_t compute_fault_flags(
    const hub_status_t *current,
    const hub_status_t *previous,
    TickType_t now_ticks,
    TickType_t *last_sensor_change,
    TickType_t *last_telemetry_change
) {
    uint32_t flags = 0u;
    uint32_t sample_period_ms = 1000u / (SENSOR_HUB_SAMPLE_RATE_HZ == 0 ? 1u : SENSOR_HUB_SAMPLE_RATE_HZ);
    uint32_t sensor_stale_ms = sample_period_ms * 4u;
    uint32_t telemetry_stale_ms = SENSOR_HUB_TELEMETRY_INTERVAL_MS * 4u;
    TickType_t sensor_stale_threshold;
    TickType_t telemetry_stale_threshold;

    if (sample_period_ms == 0u) {
        sample_period_ms = 1u;
    }
    if (sensor_stale_ms < 2000u) {
        sensor_stale_ms = 2000u;
    }
    if (telemetry_stale_ms < 2000u) {
        telemetry_stale_ms = 2000u;
    }

    sensor_stale_threshold = pdMS_TO_TICKS(sensor_stale_ms);
    telemetry_stale_threshold = pdMS_TO_TICKS(telemetry_stale_ms);

    if (current->sensor_task_heartbeat != previous->sensor_task_heartbeat) {
        *last_sensor_change = now_ticks;
    }
    if (current->telemetry_task_heartbeat != previous->telemetry_task_heartbeat) {
        *last_telemetry_change = now_ticks;
    }

    if ((now_ticks - *last_sensor_change) > sensor_stale_threshold) {
        flags |= SENSOR_HUB_FAULT_SENSOR_STALE;
    }
    if ((now_ticks - *last_telemetry_change) > telemetry_stale_threshold) {
        flags |= SENSOR_HUB_FAULT_SERIAL_STALE;
    }
    if (current->queue_overflows > previous->queue_overflows) {
        flags |= SENSOR_HUB_FAULT_QUEUE_OVERFLOW;
    }
    if (current->sensor_failures > previous->sensor_failures) {
        flags |= SENSOR_HUB_FAULT_SENSOR_FAILURE;
    }

    return flags;
}

static void fault_task(void *unused) {
    hub_status_t previous = {0};
    TickType_t last_sensor_change = xTaskGetTickCount();
    TickType_t last_telemetry_change = xTaskGetTickCount();
    (void)unused;

    for (;;) {
        hub_status_t current = hub_state_snapshot();
        TickType_t now = xTaskGetTickCount();
        uint32_t flags = compute_fault_flags(
            &current,
            &previous,
            now,
            &last_sensor_change,
            &last_telemetry_change
        );

        hub_state_set_fault_flags(flags);
        previous = current;
        hub_state_note_fault_heartbeat();

#if SENSOR_HUB_ENABLE_WATCHDOG
        watchdog_update();
#endif

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

static void print_boot_banner(void) {
    printf(
        "{\"boot\":\"pico-rtos-sensor-hub\",\"mock_mode\":%s,\"sample_rate_hz\":%d,"
        "\"telemetry_interval_ms\":%d,\"queue_length\":%d,\"ring_capacity\":%d}\n",
        sensor_source_is_mock_mode() ? "true" : "false",
        SENSOR_HUB_SAMPLE_RATE_HZ,
        SENSOR_HUB_TELEMETRY_INTERVAL_MS,
        SENSOR_HUB_QUEUE_LENGTH,
        SENSOR_HUB_RING_CAPACITY
    );
    fflush(stdout);
}

int app_runtime_run(void) {
    BaseType_t sensor_task_created;
    BaseType_t telemetry_task_created;
    BaseType_t heartbeat_task_created;
    BaseType_t fault_task_created;

    stdio_init_all();
    sleep_ms(1200);

    hub_state_init();
    sensor_source_init();
    ring_buffer_init(&g_app.ring);
    g_app.ring_mutex = xSemaphoreCreateMutex();
    g_app.sample_queue = xQueueCreate(SENSOR_HUB_QUEUE_LENGTH, sizeof(sensor_sample_t));

    if (watchdog_caused_reboot()) {
        hub_state_increment_watchdog_reset();
    }

#if SENSOR_HUB_ENABLE_WATCHDOG
    watchdog_enable(6000, true);
#endif

    configASSERT(g_app.ring_mutex != NULL);
    configASSERT(g_app.sample_queue != NULL);

    print_boot_banner();

    sensor_task_created = xTaskCreate(sensor_task, "sensor", 512, NULL, 3, NULL);
    telemetry_task_created = xTaskCreate(telemetry_task, "telemetry", 768, NULL, 2, NULL);
    heartbeat_task_created = xTaskCreate(heartbeat_task, "heartbeat", 256, NULL, 1, NULL);
    fault_task_created = xTaskCreate(fault_task, "fault", 384, NULL, 2, NULL);

    configASSERT(sensor_task_created == pdPASS);
    configASSERT(telemetry_task_created == pdPASS);
    configASSERT(heartbeat_task_created == pdPASS);
    configASSERT(fault_task_created == pdPASS);

    vTaskStartScheduler();

    while (true) {
    }
}
