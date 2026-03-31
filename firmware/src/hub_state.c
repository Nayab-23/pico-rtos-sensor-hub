#include "hub_state.h"

#include "FreeRTOS.h"
#include "task.h"

static hub_status_t g_status;

static void hub_state_with_lock(void (*mutator)(hub_status_t *)) {
    taskENTER_CRITICAL();
    mutator(&g_status);
    taskEXIT_CRITICAL();
}

static void set_sensor(hub_status_t *status) { status->sensor_task_heartbeat++; }
static void set_telemetry(hub_status_t *status) { status->telemetry_task_heartbeat++; }
static void set_blink(hub_status_t *status) { status->heartbeat_task_heartbeat++; }
static void set_fault(hub_status_t *status) { status->fault_task_heartbeat++; }
static void set_queue_overflow(hub_status_t *status) { status->queue_overflows++; }
static void set_serial_disconnect(hub_status_t *status) { status->serial_disconnects++; }
static void set_sensor_failure(hub_status_t *status) { status->sensor_failures++; }
static void set_watchdog_reset(hub_status_t *status) { status->watchdog_resets++; }

void hub_state_init(void) {
    taskENTER_CRITICAL();
    g_status = (hub_status_t){0};
    taskEXIT_CRITICAL();
}

void hub_state_note_sensor_heartbeat(void) { hub_state_with_lock(set_sensor); }
void hub_state_note_telemetry_heartbeat(void) { hub_state_with_lock(set_telemetry); }
void hub_state_note_blink_heartbeat(void) { hub_state_with_lock(set_blink); }
void hub_state_note_fault_heartbeat(void) { hub_state_with_lock(set_fault); }
void hub_state_increment_queue_overflow(void) { hub_state_with_lock(set_queue_overflow); }
void hub_state_increment_serial_disconnect(void) { hub_state_with_lock(set_serial_disconnect); }
void hub_state_increment_sensor_failure(void) { hub_state_with_lock(set_sensor_failure); }
void hub_state_increment_watchdog_reset(void) { hub_state_with_lock(set_watchdog_reset); }

void hub_state_set_fault_flags(uint32_t flags) {
    taskENTER_CRITICAL();
    g_status.last_fault_flags = flags;
    taskEXIT_CRITICAL();
}

hub_status_t hub_state_snapshot(void) {
    hub_status_t snapshot;
    taskENTER_CRITICAL();
    snapshot = g_status;
    taskEXIT_CRITICAL();
    return snapshot;
}
