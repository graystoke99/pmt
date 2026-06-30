# Project Plan

## Confirmed decisions

- The board has a fixed number and order of columns, but column titles are editable.
- The AI may create cards, edit cards, move cards, and rename columns.
- Initial sign-in may use a temporary lightweight approach before backend-backed auth behavior is added.
- SQLite is the persisted store. JSON is the board payload format used for API responses, schema modeling, and AI exchange.
- Docker will run separate frontend and backend containers.

## Part 1: Plan

Goal: establish the implementation baseline, document the current frontend, and get plan approval before feature work begins.

Checklist:

- [x] Review top-level instructions in AGENTS.md.
- [x] Review the starting plan in this document.
- [x] Review the existing frontend structure and tests.
- [x] Create frontend/AGENTS.md describing the existing frontend-only demo.
- [x] Expand this plan with concrete tasks, tests, and success criteria.
- [x] Get user approval for this plan before implementation starts.

Tests:

- Manual review of this document for completeness and sequencing.
- Manual review of frontend/AGENTS.md for accuracy against the current codebase.

Success criteria:

- The sequence of work is clear enough to execute without inventing requirements mid-stream.
- The current frontend baseline is documented.
- The user explicitly approves the plan before implementation work starts.

## Part 2: Scaffolding

Goal: stand up the initial multi-container local environment with a minimal backend and a separately running frontend.

Checklist:

- [x] Add Docker assets for separate frontend and backend containers.
- [x] Add a compose file to run both containers together locally.
- [x] Scaffold backend/ as a FastAPI service using uv for dependency management.
- [x] Add a minimal backend HTML or JSON smoke endpoint to prove the backend is running.
- [x] Add a minimal API route that the frontend or a test client can call successfully.
- [x] Add start and stop scripts for Windows, macOS, and Linux in scripts/.
- [x] Document how to run the stack locally.

Tests:

- Build both containers successfully.
- Start the compose stack successfully.
- Confirm the frontend container is reachable in a browser.
- Confirm the backend health or smoke endpoint returns success.
- Confirm an API call from outside the backend container returns the expected response.

Success criteria:

- A new developer can run one documented local command flow and get both containers up.
- The frontend and backend are independently reachable.
- The backend is proven reachable through an API response, not just container startup logs.

## Part 3: Add in Frontend

Goal: wire the existing demo frontend into the project runtime without changing its core demo behavior.

Checklist:

- [x] Ensure the current Next.js app builds cleanly for containerized local use.
- [x] Make the frontend container serve the current statically built Kanban demo at /.
- [x] Preserve existing drag-and-drop, rename, add-card, and delete-card behavior.
- [x] Verify the current visual styling survives the static export setup.
- [x] Keep or tighten the current unit and e2e test coverage for the demo behavior.

Tests:

- Frontend production build passes.
- Existing unit tests pass.
- Existing Playwright tests pass against the containerized frontend.
- Manual browser check confirms the board renders and interactions still work.

Success criteria:

- The demo board loads from the frontend container at /.
- No current frontend behavior regresses.
- The frontend remains test-backed before backend integration begins.

## Part 4: Add in a fake user sign in experience

Goal: require a simple sign-in gate before the Kanban is shown.

Checklist:

- [x] Add a login screen shown before access to the board.
- [x] Accept only the MVP credentials: user / password.
- [x] Store signed-in state using the simplest acceptable temporary approach.
- [x] Add a logout flow that clears signed-in state and returns to the login screen.
- [x] Prevent unauthenticated access to the board route in the frontend flow.

Tests:

- Unit or component tests for valid and invalid sign-in attempts.
- Integration or e2e test proving login unlocks the board.
- Integration or e2e test proving logout returns to the login screen.
- Manual check for page refresh behavior with the temporary auth state.

Success criteria:

- Unauthenticated users cannot use the board UI.
- The accepted credentials work reliably.
- Logout fully clears the session behavior introduced in this step.

## Part 5: Database modeling

Goal: define the persisted data model and document how JSON board data maps into SQLite.

Checklist:

- [x] Propose the SQLite schema for users, board state, and chat history if needed.
- [x] Define the JSON board payload shape used by the frontend and AI integration.
- [x] Decide whether board state is normalized across tables or persisted as a board JSON document plus metadata.
- [x] Document migration and database initialization expectations.
- [x] Write the database design doc in docs/.
- [x] Get user sign-off before backend persistence work begins.

Tests:

- Manual schema review for coverage of known requirements.
- Verify the JSON shape supports column CRUD, card CRUD, and card moves.

Success criteria:

- The persistence model is simple and supports all MVP board operations.
- The API payload shape is explicitly documented.
- The user approves the approach before implementation.

## Part 6: Backend

Goal: implement persistent board APIs on FastAPI backed by SQLite.

Checklist:

- [x] Add backend configuration loading, including database path and environment variables.
- [x] Persist the SQLite file outside the container layer so local data survives container recreation.
- [x] Create database initialization on startup if the SQLite file does not exist.
- [x] Seed the default user and an initial board where needed.
- [x] Add board-level CRUD endpoints for the signed-in user's board.
- [x] Add column CRUD endpoints scoped to the signed-in user's board.
- [x] Add card CRUD endpoints scoped to the signed-in user's board.
- [x] Support card move operations across columns while preserving stored column order.
- [x] Decide which operations use full-resource replacement versus targeted patch-style updates, and document that choice in the backend API design.
- [x] Add request and response models with validation.
- [x] Add backend unit tests for the persistence and API layers.

Implementation notes:

- Keep MVP backend user resolution simple: Part 6 should operate on the seeded `user` account until backend-backed auth is introduced later.
- Store the canonical board state in `boards.board_json` and apply all column and card operations by loading, mutating, validating, and rewriting that single document.
- Prefer targeted resource endpoints for frontend ergonomics, while still performing full-document writes internally.
- Recommended initial endpoint set: `GET /api/board`, `POST /api/columns`, `PATCH /api/columns/{columnId}`, `DELETE /api/columns/{columnId}`, `POST /api/cards`, `PATCH /api/cards/{cardId}`, `DELETE /api/cards/{cardId}`, and `POST /api/cards/{cardId}/move`.
- Default the SQLite path to an app-local data directory such as `/app/data/app.db`, with an overrideable environment variable for local and container use.

Tests:

- Backend unit tests for schema initialization.
- Backend unit tests for board create, read, update, and delete behavior.
- Backend unit tests for column create, read, update, and delete behavior.
- Backend unit tests for card create, read, update, and delete behavior.
- Backend unit tests for moving a card between columns.
- Backend tests for invalid payload handling.
- Manual API smoke tests against a local running backend.

Success criteria:

- The backend creates its database automatically.
- Board, column, and card resources can be created, retrieved, updated, and deleted reliably for a user.
- Card moves and column renames behave correctly without breaking board integrity.
- Invalid requests fail predictably with clear validation errors.

## Part 7: Frontend + Backend

Goal: replace local in-memory board state with backend-backed persistence.

Checklist:

- [x] Add frontend API client code for board fetch and board update operations.
- [x] Load the signed-in user's board from the backend.
- [x] Persist board changes for rename, add, delete, and move operations.
- [x] Add loading and error states that stay simple and unobtrusive.
- [x] Ensure refresh retains the latest saved board state.

Tests:

- Frontend integration tests for loading persisted board data.
- Frontend integration tests for persisting board edits.
- E2E test proving changes survive a page refresh.
- Manual verification of failure handling when the backend is unavailable.

Success criteria:

- The board is no longer frontend-only state.
- Core board interactions persist across reloads.
- Failures surface clearly without corrupting the UI state.

## Part 8: AI connectivity

Goal: prove that the backend can call OpenRouter successfully.

Checklist:

- [ ] Add backend configuration for OPENROUTER_API_KEY, reading the key from the project root .env file.
- [ ] Configure the backend to use the specified OpenRouter model: `openai/gpt-oss-120b (free)`.
- [ ] Implement a small OpenRouter client wrapper in the backend.
- [ ] Add a backend-only connectivity test path or script that asks "2+2".
- [ ] Handle missing credentials and upstream failures cleanly.
- [ ] Document that OPENROUTER_API_KEY must be supplied via the project root .env file for local development.

Tests:

- Automated or manual connectivity check that returns the expected answer to "2+2".
- Backend tests for missing API key behavior when the project root .env value is absent or unreadable.
- Backend tests for upstream error translation where practical.

Success criteria:

- The backend can read OPENROUTER_API_KEY from the project root .env file and make a successful OpenRouter request using `openai/gpt-oss-120b (free)`.
- Misconfiguration is reported clearly.
- Connectivity is proven before AI-driven board mutation is attempted.

## Part 9: Structured AI board updates

Goal: send board context and conversation history to the AI and consume structured results safely.

Checklist:

- [ ] Define the structured output schema for chat reply plus optional board update.
- [ ] Include the current board JSON and conversation history in the backend AI request.
- [ ] Parse and validate AI responses before applying updates.
- [ ] Support no-op AI replies that answer the user without changing the board.
- [ ] Persist AI-approved board updates through the same backend persistence path.
- [ ] Add tests around schema validation and update application.

Tests:

- Unit tests for structured output parsing.
- Unit tests for valid board update application.
- Unit tests for invalid or partial AI output rejection.
- Manual or mocked end-to-end test for an AI instruction that changes the board.

Success criteria:

- AI responses are schema-validated before touching persisted data.
- Board updates and plain chat replies are both supported.
- Invalid AI output fails safely.

## Part 10: AI chat sidebar

Goal: add the AI chat UI and keep board state in sync when AI applies changes.

Checklist:

- [ ] Design and add a sidebar chat interface that fits the existing visual system.
- [ ] Add message history rendering and message submission UX.
- [ ] Call the backend AI endpoint from the frontend.
- [ ] Refresh or reconcile board state automatically when AI updates are applied.
- [ ] Keep the chat flow usable on desktop and mobile widths.
- [ ] Add frontend tests for chat rendering and board refresh behavior.

Tests:

- Component or integration tests for chat submission and response rendering.
- Integration tests for applying an AI-generated board update to the UI.
- E2E test covering a realistic chat flow.
- Manual responsive check for sidebar behavior.

Success criteria:

- Users can chat with the AI from the main app UI.
- AI-triggered board updates appear automatically without manual reload.
- The new UI feels consistent with the current product direction and remains simple.

## Execution notes

- Work should proceed in order unless an earlier part needs a small refactor to support the next one cleanly.
- Part 1 and Part 5 both require explicit user approval gates.
- Keep the implementation simple. Prefer direct data flow and small abstractions over generalized frameworks.