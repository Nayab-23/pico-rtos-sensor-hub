#ifndef HUB_STATE_H
#define HUB_STATE_H

#include "sensor_hub.h"

void hub_state_init(void);
void hub_state_note_sensor_heartbeat(void);
void hub_state_note_telemetry_heartbeat(void);
void hub_state_note_blink_heartbeat(void);
void hub_state_note_fault_heartbeat(void);
void hub_state_increment_queue_overflow(void);
void hub_state_increment_serial_disconnect(void);
void hub_state_increment_sensor_failure(void);
void hub_state_increment_watchdog_reset(void);
void hub_state_set_fault_flags(uint32_t flags);
hub_status_t hub_state_snapshot(void);

#endif
