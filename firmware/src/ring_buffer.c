#include "ring_buffer.h"

void ring_buffer_init(sample_ring_buffer_t *buffer) {
    buffer->head = 0;
    buffer->count = 0;
}

bool ring_buffer_push(sample_ring_buffer_t *buffer, const sensor_sample_t *sample) {
    if (buffer == NULL || sample == NULL) {
        return false;
    }
    buffer->entries[buffer->head] = *sample;
    buffer->head = (buffer->head + 1u) % SENSOR_HUB_RING_CAPACITY;
    if (buffer->count < SENSOR_HUB_RING_CAPACITY) {
        buffer->count++;
    }
    return true;
}

bool ring_buffer_latest(const sample_ring_buffer_t *buffer, sensor_sample_t *sample_out) {
    if (buffer == NULL || sample_out == NULL || buffer->count == 0) {
        return false;
    }
    size_t latest_index = (buffer->head + SENSOR_HUB_RING_CAPACITY - 1u) % SENSOR_HUB_RING_CAPACITY;
    *sample_out = buffer->entries[latest_index];
    return true;
}

size_t ring_buffer_count(const sample_ring_buffer_t *buffer) {
    return buffer ? buffer->count : 0u;
}
