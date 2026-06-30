from __future__ import annotations

from uuid import uuid4

from app.db import DEFAULT_BOARD_ID, Database
from app.schemas import (
    BoardCreateRequest,
    BoardDocumentModel,
    BoardMoveCardRequest,
    BoardReplaceRequest,
    BoardResponse,
    CardCreateRequest,
    CardModel,
    CardUpdateRequest,
    ColumnCreateRequest,
    ColumnModel,
    ColumnUpdateRequest,
)


class NotFoundError(Exception):
    pass


class BoardValidationError(Exception):
    pass


def _build_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


def _find_column_index(columns: list[ColumnModel], column_id: str) -> int:
    for index, column in enumerate(columns):
        if column.id == column_id:
            return index
    raise NotFoundError(f"Column '{column_id}' was not found.")


def _find_card_column(columns: list[ColumnModel], card_id: str) -> tuple[int, int]:
    for column_index, column in enumerate(columns):
        for card_index, current_card_id in enumerate(column.card_ids):
            if current_card_id == card_id:
                return column_index, card_index
    raise NotFoundError(f"Card '{card_id}' was not found.")


def validate_board_document(board_document: BoardDocumentModel) -> None:
    seen_column_ids: set[str] = set()
    referenced_card_ids: list[str] = []

    for column in board_document.columns:
        if column.id in seen_column_ids:
            raise BoardValidationError(f"Duplicate column id '{column.id}'.")
        seen_column_ids.add(column.id)
        referenced_card_ids.extend(column.card_ids)

    if len(referenced_card_ids) != len(set(referenced_card_ids)):
        raise BoardValidationError("Each card must appear in exactly one column.")

    card_ids = set(board_document.cards.keys())
    for card_id in referenced_card_ids:
        if card_id not in card_ids:
            raise BoardValidationError(f"Column references unknown card '{card_id}'.")

    orphan_cards = card_ids.difference(referenced_card_ids)
    if orphan_cards:
        orphan_card_list = ", ".join(sorted(orphan_cards))
        raise BoardValidationError(f"Cards without a column are invalid: {orphan_card_list}.")

    for card_id, card in board_document.cards.items():
        if card.id != card_id:
            raise BoardValidationError(f"Card key '{card_id}' does not match payload id '{card.id}'.")


class BoardService:
    def __init__(self, database: Database):
        self.database = database

    def _load_board(self) -> BoardResponse:
        try:
            return self.database.read_board_response()
        except LookupError as exc:
            raise NotFoundError(str(exc)) from exc

    def _save_board(self, board: BoardResponse) -> BoardResponse:
        board_document = BoardDocumentModel(columns=board.columns, cards=board.cards)
        validate_board_document(board_document)
        return self.database.upsert_board(
            board_id=board.id,
            name=board.name,
            board_document=board_document.model_dump(mode="json", by_alias=True),
        )

    def get_board(self) -> BoardResponse:
        return self._load_board()

    def create_board(self, request: BoardCreateRequest) -> BoardResponse:
        if self.database.fetch_board_row() is not None:
            raise BoardValidationError("A board already exists for the MVP user.")

        board_document = BoardDocumentModel(columns=request.columns, cards=request.cards)
        validate_board_document(board_document)
        return self.database.upsert_board(
            board_id=DEFAULT_BOARD_ID,
            name=request.name,
            board_document=board_document.model_dump(mode="json", by_alias=True),
        )

    def replace_board(self, request: BoardReplaceRequest) -> BoardResponse:
        board = self._load_board()
        board.name = request.name
        board.columns = request.columns
        board.cards = request.cards
        return self._save_board(board)

    def delete_board(self) -> None:
        self._load_board()
        self.database.delete_board()

    def create_column(self, request: ColumnCreateRequest) -> BoardResponse:
        board = self._load_board()
        board.columns.append(
            ColumnModel(id=_build_id("col"), title=request.title, cardIds=[])
        )
        return self._save_board(board)

    def update_column(self, column_id: str, request: ColumnUpdateRequest) -> BoardResponse:
        board = self._load_board()
        column_index = _find_column_index(board.columns, column_id)
        board.columns[column_index].title = request.title
        return self._save_board(board)

    def delete_column(self, column_id: str) -> BoardResponse:
        board = self._load_board()
        column_index = _find_column_index(board.columns, column_id)
        column = board.columns[column_index]
        if column.card_ids:
            raise BoardValidationError("Delete or move all cards out of a column before deleting it.")
        del board.columns[column_index]
        return self._save_board(board)

    def create_card(self, request: CardCreateRequest) -> BoardResponse:
        board = self._load_board()
        column_index = _find_column_index(board.columns, request.column_id)
        card_id = _build_id("card")
        details = request.details or "No details yet."
        board.cards[card_id] = CardModel(id=card_id, title=request.title, details=details)
        board.columns[column_index].card_ids.append(card_id)
        return self._save_board(board)

    def update_card(self, card_id: str, request: CardUpdateRequest) -> BoardResponse:
        board = self._load_board()
        if card_id not in board.cards:
            raise NotFoundError(f"Card '{card_id}' was not found.")
        card = board.cards[card_id]
        if request.title is not None:
            card.title = request.title
        if request.details is not None:
            card.details = request.details or "No details yet."
        return self._save_board(board)

    def delete_card(self, card_id: str) -> BoardResponse:
        board = self._load_board()
        column_index, card_index = _find_card_column(board.columns, card_id)
        del board.columns[column_index].card_ids[card_index]
        del board.cards[card_id]
        return self._save_board(board)

    def move_card(self, card_id: str, request: BoardMoveCardRequest) -> BoardResponse:
        board = self._load_board()
        source_column_index, source_card_index = _find_card_column(board.columns, card_id)
        target_column_index = _find_column_index(board.columns, request.target_column_id)

        board.columns[source_column_index].card_ids.pop(source_card_index)
        target_card_ids = board.columns[target_column_index].card_ids
        insert_index = request.target_index
        if insert_index is None or insert_index > len(target_card_ids):
            insert_index = len(target_card_ids)
        target_card_ids.insert(insert_index, card_id)
        return self._save_board(board)