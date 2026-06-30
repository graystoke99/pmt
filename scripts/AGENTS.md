## Scripts overview

This folder contains local environment helper scripts for Windows, macOS, and Linux.

## Current scripts

- `start.ps1` starts the Docker compose stack on Windows PowerShell
- `stop.ps1` stops the Docker compose stack on Windows PowerShell
- `start.sh` starts the Docker compose stack on macOS and Linux shells
- `stop.sh` stops the Docker compose stack on macOS and Linux shells

## Scope

- Keep scripts small and predictable
- Prefer Docker compose as the single entry point for local stack management
- Print the URLs a developer needs after startup