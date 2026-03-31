#include "sensor_source.h"

#include <math.h>
#include <stdbool.h>

#include "hardware/adc.h"

static bool g_mock_mode = true;
static uint32_t g_sequence = 0;

void sensor_source_init(void) {
#if SENSOR_HUB_USE_MOCK_SENSORS
    g_mock_mode = true;
#else
    g_mock_mode = false;
    adc_init();
    adc_set_temp_sensor_enabled(true);
    adc_select_input(4);
#endif
}

static void fill_mock_sample(sensor_sample_t *sample, uint32_t uptime_ms) {
    float t = (float)uptime_ms / 1000.0f;
    sample->temperature_c = 23.0f + 2.8f * sinf(t / 7.0f);
    sample->humidity_pct = 44.0f + 8.0f * cosf(t / 5.0f);
    sample->light_lux = 150.0f + 80.0f * (sinf(t / 3.0f) + 1.0f);
    sample->voltage_v = 3.25f + 0.05f * sinf(t / 11.0f);
}

static void fill_internal_temp_sample(sensor_sample_t *sample) {
    const float conversion = 3.3f / (1u << 12);
    uint16_t raw = adc_read();
    float voltage = raw * conversion;
    sample->temperature_c = 27.0f - (voltage - 0.706f) / 0.001721f;
    sample->humidity_pct = 0.0f;
    sample->light_lux = 0.0f;
    sample->voltage_v = voltage;
}

bool sensor_source_read(sensor_sample_t *sample, uint32_t uptime_ms) {
    if (sample == NULL) {
        return false;
    }

    *sample = (sensor_sample_t){0};
    sample->sequence = ++g_sequence;
    sample->uptime_ms = uptime_ms;
    sample->mock_mode = g_mock_mode;

    if (g_mock_mode) {
        fill_mock_sample(sample, uptime_ms);
    } else {
        fill_internal_temp_sample(sample);
    }

    return true;
}

bool sensor_source_is_mock_mode(void) {
    return g_mock_mode;
}
