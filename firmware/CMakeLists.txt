cmake_minimum_required(VERSION 3.20)

set(PICO_SDK_FETCH_FROM_GIT ON CACHE BOOL "Fetch Pico SDK automatically")
set(PICO_SDK_FETCH_FROM_GIT_TAG "2.1.1" CACHE STRING "Pico SDK tag")
include(cmake/pico_sdk_import.cmake)

project(pico_rtos_sensor_hub C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)

set(PICO_BOARD "pico" CACHE STRING "Target Pico board")
option(SENSOR_HUB_USE_MOCK_SENSORS "Use mock sensor data instead of real readings" ON)
option(SENSOR_HUB_ENABLE_WATCHDOG "Enable hardware watchdog feeding" OFF)
set(SENSOR_HUB_SAMPLE_RATE_HZ "10" CACHE STRING "Sensor sampling rate")
set(SENSOR_HUB_TELEMETRY_INTERVAL_MS "500" CACHE STRING "Telemetry output interval")
set(SENSOR_HUB_QUEUE_LENGTH "16" CACHE STRING "Sample queue depth")
set(SENSOR_HUB_RING_CAPACITY "64" CACHE STRING "Ring buffer capacity")

pico_sdk_init()

FetchContent_Declare(
    freertos_kernel
    GIT_REPOSITORY https://github.com/FreeRTOS/FreeRTOS-Kernel.git
    GIT_TAG V10.6.2
    GIT_SHALLOW TRUE
)
FetchContent_GetProperties(freertos_kernel)
if (NOT freertos_kernel_POPULATED)
    FetchContent_Populate(freertos_kernel)
endif ()

set(FREERTOS_PORT GCC_RP2040 CACHE STRING "FreeRTOS port")
set(FREERTOS_HEAP 4 CACHE STRING "FreeRTOS heap implementation")

add_library(freertos_config INTERFACE)
target_include_directories(
    freertos_config SYSTEM
    INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/config
        ${CMAKE_CURRENT_LIST_DIR}/include
)
target_compile_definitions(
    freertos_config
    INTERFACE
        projCOVERAGE_TEST=0
)

add_subdirectory(${freertos_kernel_SOURCE_DIR} ${CMAKE_BINARY_DIR}/freertos_kernel)

add_executable(pico_rtos_sensor_hub
    src/main.c
    src/hub_state.c
    src/ring_buffer.c
    src/sensor_source.c
    src/telemetry.c
)

target_include_directories(
    pico_rtos_sensor_hub
    PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}/include
        ${CMAKE_CURRENT_LIST_DIR}/config
)

target_compile_definitions(
    pico_rtos_sensor_hub
    PRIVATE
        SENSOR_HUB_USE_MOCK_SENSORS=$<BOOL:${SENSOR_HUB_USE_MOCK_SENSORS}>
        SENSOR_HUB_ENABLE_WATCHDOG=$<BOOL:${SENSOR_HUB_ENABLE_WATCHDOG}>
        SENSOR_HUB_SAMPLE_RATE_HZ=${SENSOR_HUB_SAMPLE_RATE_HZ}
        SENSOR_HUB_TELEMETRY_INTERVAL_MS=${SENSOR_HUB_TELEMETRY_INTERVAL_MS}
        SENSOR_HUB_QUEUE_LENGTH=${SENSOR_HUB_QUEUE_LENGTH}
        SENSOR_HUB_RING_CAPACITY=${SENSOR_HUB_RING_CAPACITY}
        PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS=0
)

target_link_libraries(
    pico_rtos_sensor_hub
    PRIVATE
        pico_stdlib
        hardware_adc
        hardware_watchdog
        hardware_gpio
        freertos_kernel
        m
)

pico_enable_stdio_usb(pico_rtos_sensor_hub 1)
pico_enable_stdio_uart(pico_rtos_sensor_hub 0)
pico_add_extra_outputs(pico_rtos_sensor_hub)
