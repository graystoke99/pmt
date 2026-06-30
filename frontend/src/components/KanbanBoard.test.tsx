import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData, type PersistedBoard } from "@/lib/kanban";
import * as boardApi from "@/lib/boardApi";

vi.mock("@/lib/boardApi", async () => {
  const actual = await vi.importActual<typeof import("@/lib/boardApi")>("@/lib/boardApi");
  return {
    ...actual,
    getBoard: vi.fn(),
    updateColumn: vi.fn(),
    createCard: vi.fn(),
    deleteCard: vi.fn(),
    moveCard: vi.fn(),
  };
});

const createBoard = (overrides?: Partial<PersistedBoard>): PersistedBoard => ({
  id: "board-1",
  userId: "user-1",
  name: "Kanban Studio",
  updatedAt: "2026-06-30T12:00:00Z",
  ...initialData,
  ...overrides,
});

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(boardApi.getBoard).mockResolvedValue(createBoard());
  });

  it("renders five columns", () => {
    render(<KanbanBoard />);
    return waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
  });

  it("renames a column", async () => {
    const renamedBoard = createBoard({
      columns: initialData.columns.map((column) =>
        column.id === "col-backlog" ? { ...column, title: "New Name" } : column
      ),
    });
    vi.mocked(boardApi.updateColumn).mockResolvedValue(renamedBoard);

    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
    await userEvent.tab();

    await waitFor(() => {
      expect(boardApi.updateColumn).toHaveBeenCalledWith("col-backlog", "New Name");
    });
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    const addedBoard = createBoard({
      columns: initialData.columns.map((column, index) =>
        index === 0
          ? { ...column, cardIds: [...column.cardIds, "card-new"] }
          : column
      ),
      cards: {
        ...initialData.cards,
        "card-new": {
          id: "card-new",
          title: "New card",
          details: "Notes",
        },
      },
    });
    vi.mocked(boardApi.createCard).mockResolvedValue(addedBoard);
    vi.mocked(boardApi.deleteCard).mockResolvedValue(createBoard());

    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);
    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(await within(column).findByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    await waitFor(() => {
      expect(boardApi.deleteCard).toHaveBeenCalledWith("card-new");
    });
    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });

  it("shows a retry message when the board fails to load", async () => {
    vi.mocked(boardApi.getBoard).mockRejectedValue(new Error("Backend offline"));

    render(<KanbanBoard />);

    expect(await screen.findByText("Backend offline")).toBeVisible();
    expect(screen.getByRole("button", { name: "Retry" })).toBeVisible();
  });
});
