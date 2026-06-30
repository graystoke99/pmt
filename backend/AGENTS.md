## Backend overview

This directory contains the FastAPI backend for the project management MVP.

## Current scope

- FastAPI application entry point in `app/main.py`
- SQLite-backed board persistence with automatic schema initialization and seeding
- Board, column, and card API endpoints for the single MVP user
- Health and hello API endpoints for smoke testing
- Backend API and persistence tests under `tests/`

## Current responsibilities

- Expose the backend service on port `8000`
- Initialize the SQLite database automatically on startup
- Serve the persisted board state for the seeded MVP user
- Validate and persist board, column, and card mutations
- Keep local Docker persistence in `/app/data/app.db`

## Near-term follow-up

- Add OpenRouter integration