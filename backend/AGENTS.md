## Backend overview

This directory contains the FastAPI backend for the project management MVP.

## Current scope

- FastAPI application entry point in `app/main.py`
- Minimal scaffolding for local Docker-based development
- Health and hello API endpoints for smoke testing
- A simple HTML root page that proves the backend is running and can call its own API

## Current responsibilities

- Expose the backend service on port `8000`
- Provide a basic API surface for local verification before board persistence is added
- Establish the Python and `uv` project structure that later backend work will build on

## Near-term follow-up

- Add database initialization and persistence
- Add board, column, and card APIs
- Add OpenRouter integration