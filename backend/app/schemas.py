from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    service: str


class CardModel(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    details: str = Field(default="")


class ColumnModel(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    card_ids: list[str] = Field(alias="cardIds", default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class BoardDocumentModel(BaseModel):
    columns: list[ColumnModel]
    cards: dict[str, CardModel]


class BoardResponse(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    name: str
    columns: list[ColumnModel]
    cards: dict[str, CardModel]
    updated_at: str = Field(alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class BoardCreateRequest(BoardDocumentModel):
    name: str = Field(min_length=1, max_length=120)


class BoardReplaceRequest(BoardDocumentModel):
    name: str = Field(min_length=1, max_length=120)


class ColumnCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=80)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return value.strip()


class ColumnUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=80)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return value.strip()


class CardCreateRequest(BaseModel):
    column_id: str = Field(alias="columnId", min_length=1)
    title: str = Field(min_length=1, max_length=120)
    details: str = Field(default="", max_length=2000)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return value.strip()

    @field_validator("details")
    @classmethod
    def normalize_details(cls, value: str) -> str:
        return value.strip()


class CardUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    details: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @field_validator("details")
    @classmethod
    def normalize_details(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()


class BoardMoveCardRequest(BaseModel):
    target_column_id: str = Field(alias="targetColumnId", min_length=1)
    target_index: int | None = Field(alias="targetIndex", default=None, ge=0)

    model_config = ConfigDict(populate_by_name=True)