# Frontend overview

This directory contains the current frontend-only MVP demo for the project management app.

## Current stack

- Next.js 16 App Router
- React 19
- TypeScript
- Tailwind CSS v4 via globals.css
- dnd-kit for drag and drop
- Vitest + Testing Library for unit and component tests
- Playwright for browser tests

## Current entry points

- src/app/page.tsx renders AppShell at /.
- src/app/layout.tsx sets global fonts, metadata, and shared layout shell.
- src/app/globals.css defines the core color variables and global styling primitives.
- src/components/AppShell.tsx owns the temporary sign-in gate and switches between the login view and the board.

## Current behavior

- The app currently renders a temporary sign-in gate before loading a single persisted Kanban board from the backend.
- The accepted MVP credentials are `user` and `password`.
- Auth state is stored in browser local storage under `pm-authenticated`.
- The current demo seed starts with five columns.
- Column titles can be renamed inline.
- Cards can be dragged within a column or across columns.
- Cards can be added from the per-column add form.
- Cards can be deleted from the board.
- The board now persists through the FastAPI backend and survives page refresh.
- There is no backend-backed authentication or AI chat yet.

## Component structure

- src/components/KanbanBoard.tsx is the stateful top-level client component. It loads the persisted board, drives mutation requests, manages drag handling, and surfaces simple loading and error states.
- src/components/KanbanColumn.tsx renders a droppable column, the editable column title, the sortable card list, and the new-card form.
- src/components/KanbanCard.tsx renders a sortable card and its delete action.
- src/components/KanbanCardPreview.tsx renders the drag overlay preview.
- src/components/NewCardForm.tsx manages the add-card disclosure and form state.

## Data model

- src/lib/kanban.ts defines the in-memory board types: Card, Column, and BoardData.
- PersistedBoard represents the backend response shape used by the frontend.
- initialData still mirrors the seeded backend board for tests and shared assumptions.
- getCardMoveTarget computes the backend move request payload for drag-and-drop.
- src/lib/boardApi.ts contains the frontend API client used to load and mutate the board.

## Testing baseline

- src/components/KanbanBoard.test.tsx covers loading the board, renaming a column, adding/removing a card, and backend load failure handling.
- src/lib/kanban.test.ts covers board utility behavior.
- src/components/AppShell.test.tsx verifies the temporary sign-in flow with backend-backed board loading.
- tests/kanban.spec.ts covers browser-level rendering, adding a card, drag-and-drop behavior, and refresh persistence expectations.

## Implementation constraints for future work

- Preserve the established color palette from the project-level AGENTS.md.
- Keep the current visual tone and avoid unnecessary UI complexity.
- Prefer small, direct changes over abstractions that are not needed for the MVP.
- When backend integration begins, avoid breaking the existing tested interactions while moving from in-memory state to persisted API-backed state.
- The board currently assumes one visible board. Future multi-user support should be introduced through data boundaries, not frontend complexity.