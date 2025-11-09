# Environment Configuration

This repository now expects each service to read its own `.env` file. These settings
control development-time networking so the apps are easy to containerize or deploy.

## llm

- `LLM_SERVER_HOST` — interface bound by the FastAPI server (`0.0.0.0` by default).
- `LLM_SERVER_PORT` — primary API port (`8000`).
- `EXECUTOR_SERVER_HOST` — interface for the executor bridge server (`0.0.0.0`).
- `EXECUTOR_SERVER_PORT` — port for the executor bridge server (`8100`).

Place these variables in `llm/.env`. The module loads `../.env` first (if present)
and then overrides with values from `llm/.env`.

## webapp

- `WEBAPP_HOST` — host interface for the Vite dev server (`0.0.0.0`).
- `WEBAPP_PORT` — port for the React webapp dev server (`5173`).
- `WEBAPP_OPEN_BROWSER` — whether Vite should open a browser window on start (`true`).
- `DOM_SNAPSHOT_WS_HOST` — host for the DOM snapshot websocket bridge (`0.0.0.0`).
- `DOM_SNAPSHOT_WS_PORT` — port for the websocket bridge (defaults to server port).
- `DOM_SNAPSHOT_WS_PATH` — websocket URL path (`/dom-snapshot`).
- `DOM_SNAPSHOT_WS_TIMEOUT_MS` — request timeout in milliseconds (`10000`).

Set these in `webapp/.env`. Existing `.env` files are respected—add any missing keys.

## iframe-content

- `IFRAME_HOST` — host interface for the Vue dev server (`0.0.0.0`).
- `IFRAME_PORT` — port for the iframe dev server (`5174`).

Store these in `iframe-content/.env`.

> Tip: when containerizing, set the same variables at runtime so the dev servers and
> websocket bridge bind to predictable addresses.

