#ifndef SENSOR_SOURCE_H
#define SENSOR_SOURCE_H

#include <stdbool.h>
#include <stdint.h>

#include "sensor_hub.h"

void sensor_source_init(void);
bool sensor_source_read(sensor_sample_t *sample, uint32_t uptime_ms);
bool sensor_source_is_mock_mode(void);

#endif
