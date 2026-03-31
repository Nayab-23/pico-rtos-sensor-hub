#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <stddef.h>

#include "sensor_hub.h"

int telemetry_format_json(
    char *buffer,
    size_t buffer_size,
    const sensor_sample_t *sample,
    const hub_status_t *status,
    size_t ring_count,
    size_t queue_depth
);

#endif
