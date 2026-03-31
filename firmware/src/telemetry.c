#include "telemetry.h"

#include <stdio.h>

int telemetry_format_json(
    char *buffer,
    size_t buffer_size,
    const sensor_sample_t *sample,
    const hub_status_t *status,
    size_t ring_count,
    size_t queue_depth
) {
    if (buffer == NULL || sample == NULL || status == NULL) {
        return -1;
    }

    return snprintf(
        buffer,
        buffer_size,
        "{\"seq\":%lu,\"uptime_ms\":%lu,\"sensor\":{\"temperature_c\":%.2f,\"humidity_pct\":%.2f,"
        "\"light_lux\":%.2f,\"voltage_v\":%.3f},\"status\":{\"mock_mode\":%s,\"queue_overflows\":%lu,"
        "\"sensor_failures\":%lu,\"serial_disconnects\":%lu,\"watchdog_resets\":%lu,\"fault_flags\":%lu,"
        "\"heartbeats\":{\"sensor\":%lu,\"telemetry\":%lu,\"heartbeat\":%lu,\"fault\":%lu}},"
        "\"buffer\":{\"ring_count\":%u,\"queue_depth\":%u}}\n",
        (unsigned long)sample->sequence,
        (unsigned long)sample->uptime_ms,
        (double)sample->temperature_c,
        (double)sample->humidity_pct,
        (double)sample->light_lux,
        (double)sample->voltage_v,
        sample->mock_mode ? "true" : "false",
        (unsigned long)status->queue_overflows,
        (unsigned long)status->sensor_failures,
        (unsigned long)status->serial_disconnects,
        (unsigned long)status->watchdog_resets,
        (unsigned long)status->last_fault_flags,
        (unsigned long)status->sensor_task_heartbeat,
        (unsigned long)status->telemetry_task_heartbeat,
        (unsigned long)status->heartbeat_task_heartbeat,
        (unsigned long)status->fault_task_heartbeat,
        (unsigned int)ring_count,
        (unsigned int)queue_depth
    );
}
