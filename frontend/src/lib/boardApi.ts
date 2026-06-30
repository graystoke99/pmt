import type { BoardData, PersistedBoard } from "@/lib/kanban";

type BoardResponse = PersistedBoard;

const DEFAULT_API_PORT = "8000";

const getApiBaseUrl = () => {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (configured) {
    return configured.replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:${DEFAULT_API_PORT}`;
  }

  return `http://127.0.0.1:${DEFAULT_API_PORT}`;
};

const getErrorMessage = async (response: Response) => {
  try {
    const payload = (await response.json()) as { detail?: string };
    if (payload.detail) {
      return payload.detail;
    }
  } catch {
    return `Request failed with status ${response.status}.`;
  }

  return `Request failed with status ${response.status}.`;
};

const request = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
};

export const getBoard = () => request<BoardResponse>("/api/board");

export const updateColumn = (columnId: string, title: string) =>
  request<BoardResponse>(`/api/columns/${columnId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });

export const createCard = (columnId: string, title: string, details: string) =>
  request<BoardResponse>("/api/cards", {
    method: "POST",
    body: JSON.stringify({ columnId, title, details }),
  });

export const deleteCard = (cardId: string) =>
  request<BoardResponse>(`/api/cards/${cardId}`, {
    method: "DELETE",
  });

export const moveCard = (
  cardId: string,
  targetColumnId: string,
  targetIndex: number
) =>
  request<BoardResponse>(`/api/cards/${cardId}/move`, {
    method: "POST",
    body: JSON.stringify({ targetColumnId, targetIndex }),
  });

export const toBoardData = (board: PersistedBoard): BoardData => ({
  columns: board.columns,
  cards: board.cards,
});