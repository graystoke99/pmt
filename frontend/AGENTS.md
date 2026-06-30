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

- src/app/page.tsx renders the Kanban board directly at /.
- src/app/layout.tsx sets global fonts, metadata, and shared layout shell.
- src/app/globals.css defines the core color variables and global styling primitives.

## Current behavior

- The app currently renders a single in-memory Kanban board.
- The board has five fixed columns.
- Column titles can be renamed inline.
- Cards can be dragged within a column or across columns.
- Cards can be added from the per-column add form.
- Cards can be deleted from the board.
- There is no authentication, backend integration, persistence, or AI chat yet.

## Component structure

- src/components/KanbanBoard.tsx is the stateful top-level client component. It owns board state, drag handling, column rename behavior, add-card behavior, and delete-card behavior.
- src/components/KanbanColumn.tsx renders a droppable column, the editable column title, the sortable card list, and the new-card form.
- src/components/KanbanCard.tsx renders a sortable card and its delete action.
- src/components/KanbanCardPreview.tsx renders the drag overlay preview.
- src/components/NewCardForm.tsx manages the add-card disclosure and form state.

## Data model

- src/lib/kanban.ts defines the in-memory board types: Card, Column, and BoardData.
- initialData is the current demo seed.
- moveCard handles reordering within a column and moving cards between columns.
- createId generates client-side IDs for new cards.

## Testing baseline

- src/components/KanbanBoard.test.tsx covers rendering five columns, renaming a column, and adding/removing a card.
- src/lib/kanban.test.ts covers board utility behavior.
- tests/kanban.spec.ts covers browser-level rendering, adding a card, and drag-and-drop behavior.

## Implementation constraints for future work

- Preserve the established color palette from the project-level AGENTS.md.
- Keep the current visual tone and avoid unnecessary UI complexity.
- Prefer small, direct changes over abstractions that are not needed for the MVP.
- When backend integration begins, avoid breaking the existing tested interactions while moving from in-memory state to persisted API-backed state.
- The board currently assumes one visible board. Future multi-user support should be introduced through data boundaries, not frontend complexity.