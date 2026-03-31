#ifndef SENSOR_HUB_H
#define SENSOR_HUB_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t sequence;
    uint32_t uptime_ms;
    float temperature_c;
    float humidity_pct;
    float light_lux;
    float voltage_v;
    bool mock_mode;
    uint32_t sensor_errors;
} sensor_sample_t;

typedef struct {
    uint32_t sensor_task_heartbeat;
    uint32_t telemetry_task_heartbeat;
    uint32_t heartbeat_task_heartbeat;
    uint32_t fault_task_heartbeat;
    uint32_t queue_overflows;
    uint32_t serial_disconnects;
    uint32_t sensor_failures;
    uint32_t watchdog_resets;
    uint32_t last_fault_flags;
} hub_status_t;

#define SENSOR_HUB_FAULT_QUEUE_OVERFLOW  (1u << 0)
#define SENSOR_HUB_FAULT_SENSOR_STALE    (1u << 1)
#define SENSOR_HUB_FAULT_SENSOR_FAILURE  (1u << 2)
#define SENSOR_HUB_FAULT_SERIAL_STALE    (1u << 3)

#endif
