# Build Host Strategy

## Default Mode

The Raspberry Pi is treated as a host-side telemetry, logging, and validation station first.

Default daily workflow:

1. detect hardware
2. run simulator validation
3. review telemetry in the terminal or dashboard
4. only escalate to firmware builds when a real Pico is attached or when a firmware-specific change requires it

## Deferred Toolchain Policy

Heavy provisioning on the Pi is optional.

That includes:

- ARM cross-compiler installation
- Pico SDK retrieval
- full UF2 build verification

These steps are deferred unless one of the following is true:

- the toolchain is already installed
- a real board is attached and flashing is immediately useful
- an operator explicitly invokes the toolchain installer

## Why This Is Still Resume-Worthy

Even without a Pico attached, the project still demonstrates:

- a serial telemetry schema
- host-side parsing and persistence
- simulator-backed validation
- dashboard review
- flashing and build helper scripts
- documented hardware bring-up paths
