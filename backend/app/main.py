from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse


app = FastAPI(title="Project Management MVP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def read_root() -> str:
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


@app.get("/api/health")
def read_health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get("/api/hello")
def read_hello() -> dict[str, str]:
    return {
        "message": "Hello world from the backend API.",
        "service": "backend",
    }