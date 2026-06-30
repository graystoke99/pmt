# Local development

## Docker workflow

This project currently runs as two containers:

- Frontend at `http://localhost:3000`
- Backend at `http://localhost:8000`

The frontend container serves the statically built Next.js export.

## Start the stack

Windows PowerShell:

```powershell
./scripts/start.ps1
```

macOS or Linux:

```sh
./scripts/start.sh
```

Manual alternative:

```sh
docker compose up --build -d
```

## Stop the stack

Windows PowerShell:

```powershell
./scripts/stop.ps1
```

macOS or Linux:

```sh
./scripts/stop.sh
```

Manual alternative:

```sh
docker compose down --remove-orphans
```

## Smoke checks

- Open `http://localhost:3000` to confirm the frontend container is reachable.
- Sign in with username `user` and password `password` to access the board.
- Open `http://localhost:8000` to confirm the backend hello page renders.
- The backend root page automatically calls `/api/hello` and renders the API response in the page.
- Open `http://localhost:8000/api/health` to confirm the backend health response.

## Temporary auth note

- The current sign-in gate is frontend-only and temporary.
- Signed-in state is stored in browser local storage under the key `pm-authenticated`.
- This is only for the MVP flow in Part 4 and should be replaced when backend-backed auth is introduced.

## Frontend test commands

- Run `npm run test:unit` inside `frontend/` for component and utility coverage.
- Run `npm run playwright:install` once inside `frontend/` to install the Playwright browsers.
- Run `npm run test:e2e` inside `frontend/` to execute the browser tests against the static build flow.
- If the Playwright-managed browser cache is unreliable on the machine, set `PLAYWRIGHT_EXECUTABLE_PATH` to a real system browser executable before running `npm run test:e2e`.

Working Windows PowerShell example using the system Chrome install:

```powershell
Set-Location "c:\000 Projects\pm\pm\frontend"
$env:PLAYWRIGHT_BROWSER_NAME='chromium'
$env:PLAYWRIGHT_EXECUTABLE_PATH='C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
npm run test:e2e
```