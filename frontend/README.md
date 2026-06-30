# Kanban Studio

## Run

```bash
npm install
npm run dev
```

Sign in with username `user` and password `password`.

This login is temporary for the MVP. It is enforced in the frontend only, and the signed-in flag is stored in browser local storage under `pm-authenticated`.

## Static build

```bash
npm run build
npm run serve:static
```

## Tests

```bash
npm run test:unit
npm run playwright:install
npm run test:e2e
```

If Playwright browser cache resolution is unreliable on the machine, the e2e suite can be run against a real system Chrome install by setting `PLAYWRIGHT_EXECUTABLE_PATH` before `npm run test:e2e`.

Working Windows PowerShell example:

```powershell
Set-Location "c:\000 Projects\pm\pm\frontend"
$env:PLAYWRIGHT_BROWSER_NAME='chromium'
$env:PLAYWRIGHT_EXECUTABLE_PATH='C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
npm run test:e2e
```
