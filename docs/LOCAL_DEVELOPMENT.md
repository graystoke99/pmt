# Local development

## Docker workflow

This project currently runs as two containers:

- Frontend at `http://localhost:3000`
- Backend at `http://localhost:8000`

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
- Open `http://localhost:8000` to confirm the backend hello page renders.
- The backend root page automatically calls `/api/hello` and renders the API response in the page.
- Open `http://localhost:8000/api/health` to confirm the backend health response.