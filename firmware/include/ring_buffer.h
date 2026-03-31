#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdbool.h>
#include <stddef.h>

#include "sensor_hub.h"

typedef struct {
    sensor_sample_t entries[SENSOR_HUB_RING_CAPACITY];
    size_t head;
    size_t count;
} sample_ring_buffer_t;

void ring_buffer_init(sample_ring_buffer_t *buffer);
bool ring_buffer_push(sample_ring_buffer_t *buffer, const sensor_sample_t *sample);
bool ring_buffer_latest(const sample_ring_buffer_t *buffer, sensor_sample_t *sample_out);
size_t ring_buffer_count(const sample_ring_buffer_t *buffer);

#endif
