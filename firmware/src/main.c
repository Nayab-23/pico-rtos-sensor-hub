#include <stdio.h>

#include "pico/stdlib.h"

int main(void) {
    stdio_init_all();
    sleep_ms(1200);

    while (true) {
        printf("pico-rtos-sensor-hub firmware architecture scaffold\n");
        sleep_ms(1000);
    }
}
