from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.config import Settings, get_settings
from app.db import Database
from app.schemas import (
  BoardCreateRequest,
  BoardMoveCardRequest,
  BoardReplaceRequest,
  BoardResponse,
  CardCreateRequest,
  CardUpdateRequest,
  ColumnCreateRequest,
  ColumnUpdateRequest,
  HealthResponse,
)
from app.service import BoardService, BoardValidationError, NotFoundError


def build_root_html() -> str:
  return """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Backend Hello</title>
    <style>
      :root {
        color-scheme: light;
        font-family: "Segoe UI", sans-serif;
      }
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, #f4f8fc 0%, #ffffff 55%, #eef4fb 100%);
        color: #032147;
      }
      main {
        width: min(720px, calc(100vw - 32px));
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(3, 33, 71, 0.08);
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 18px 40px rgba(3, 33, 71, 0.12);
      }
      h1 {
        margin: 0 0 12px;
      }
      p {
        line-height: 1.6;
      }
      code {
        background: #f7f8fb;
        border-radius: 8px;
        padding: 2px 8px;
      }
      .result {
        margin-top: 24px;
        padding: 16px;
        border-radius: 16px;
        background: #f7f8fb;
        border: 1px solid rgba(3, 33, 71, 0.08);
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Hello from FastAPI</h1>
      <p>This backend scaffold is running locally in Docker.</p>
      <p>The API call below is loaded from <code>/api/hello</code> after the page renders.</p>
      <div class=\"result\" id=\"result\">Loading API response...</div>
    </main>
    <script>
      async function loadMessage() {
        const result = document.getElementById("result");
        try {
          const response = await fetch("/api/hello");
          if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
          }
          const payload = await response.json();
          result.textContent = `${payload.message} (${payload.service})`;
        } catch (error) {
          result.textContent = `API call failed: ${error.message}`;
        }
      }
      loadMessage();
    </script>
  </body>
</html>
"""


def create_app(settings: Settings | None = None) -> FastAPI:
  resolved_settings = settings or get_settings()
  database = Database(resolved_settings.database_path)

  @asynccontextmanager
  async def lifespan(_: FastAPI):
    database.initialize()
    yield

  app = FastAPI(title=resolved_settings.app_name, lifespan=lifespan)
  app.state.settings = resolved_settings
  app.state.database = database

  app.add_middleware(
    CORSMiddleware,
    allow_origins=resolved_settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  def get_service() -> BoardService:
    return BoardService(database)

  @app.get("/", response_class=HTMLResponse)
  def read_root() -> str:
    return build_root_html()

  @app.get("/api/health", response_model=HealthResponse)
  def read_health() -> HealthResponse:
    return HealthResponse(status="ok", service="backend")

  @app.get("/api/hello")
  def read_hello() -> dict[str, str]:
    return {
      "message": "Hello world from the backend API.",
      "service": "backend",
    }

  @app.get("/api/board", response_model=BoardResponse)
  def read_board(service: BoardService = Depends(get_service)) -> BoardResponse:
    return service.get_board()

  @app.post("/api/board", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
  def create_board(
    request: BoardCreateRequest,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.create_board(request)

  @app.put("/api/board", response_model=BoardResponse)
  def replace_board(
    request: BoardReplaceRequest,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.replace_board(request)

  @app.delete("/api/board", status_code=status.HTTP_204_NO_CONTENT)
  def delete_board(service: BoardService = Depends(get_service)) -> Response:
    service.delete_board()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

  @app.post("/api/columns", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
  def create_column(
    request: ColumnCreateRequest,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.create_column(request)

  @app.patch("/api/columns/{column_id}", response_model=BoardResponse)
  def update_column(
    column_id: str,
    request: ColumnUpdateRequest,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.update_column(column_id, request)

  @app.delete("/api/columns/{column_id}", response_model=BoardResponse)
  def delete_column(
    column_id: str,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.delete_column(column_id)

  @app.post("/api/cards", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
  def create_card(
    request: CardCreateRequest,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.create_card(request)

  @app.patch("/api/cards/{card_id}", response_model=BoardResponse)
  def update_card(
    card_id: str,
    request: CardUpdateRequest,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.update_card(card_id, request)

  @app.delete("/api/cards/{card_id}", response_model=BoardResponse)
  def delete_card(
    card_id: str,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.delete_card(card_id)

  @app.post("/api/cards/{card_id}/move", response_model=BoardResponse)
  def move_card(
    card_id: str,
    request: BoardMoveCardRequest,
    service: BoardService = Depends(get_service),
  ) -> BoardResponse:
    return service.move_card(card_id, request)

  @app.exception_handler(NotFoundError)
  async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
      status_code=status.HTTP_404_NOT_FOUND,
      content={"detail": str(exc)},
    )

  @app.exception_handler(BoardValidationError)
  async def handle_board_validation(_: Request, exc: BoardValidationError) -> JSONResponse:
    return JSONResponse(
      status_code=status.HTTP_409_CONFLICT,
      content={"detail": str(exc)},
    )

  return app


app = create_app()