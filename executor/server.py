import asyncio
import json
import os
from typing import Optional
from uuid import uuid4

import websockets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


def resolve_dom_snapshot_ws_url() -> str:
    explicit_url = os.getenv("DOM_SNAPSHOT_WS_URL")
    if explicit_url:
        return explicit_url

    scheme = os.getenv("DOM_SNAPSHOT_WS_SCHEME", "ws")
    host = os.getenv("DOM_SNAPSHOT_WS_HOST", "0.0.0.0")
    port = os.getenv("DOM_SNAPSHOT_WS_PORT")
    path = os.getenv("DOM_SNAPSHOT_WS_PATH", "/dom-snapshot")

    if not path.startswith("/"):
        path = f"/{path}"

    if port:
        if ":" in host and not host.startswith("["):
            return f"{scheme}://{host}{path}"
        return f"{scheme}://{host}:{port}{path}"

    return f"{scheme}://{host}{path}"


DOM_SNAPSHOT_WS_URL_DEFAULT = resolve_dom_snapshot_ws_url()
DOM_SNAPSHOT_REQUEST_TIMEOUT_DEFAULT = float(
    os.getenv("DOM_SNAPSHOT_REQUEST_TIMEOUT", "10")
)

EXECUTOR_SERVER_HOST = os.getenv("EXECUTOR_SERVER_HOST", "0.0.0.0")
EXECUTOR_SERVER_PORT = int(os.getenv("EXECUTOR_SERVER_PORT", "8100"))

app = FastAPI(title="Executor Bridge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_dom_snapshot(
    ws_url: str = DOM_SNAPSHOT_WS_URL_DEFAULT,
    timeout: float = DOM_SNAPSHOT_REQUEST_TIMEOUT_DEFAULT,
    target_client_id: Optional[str] = None,
) -> dict:
    """
    Request a DOM snapshot from the frontend websocket bridge.
    """
    request_id = str(uuid4())
    request_payload = {
        "type": "get_dom_snapshot",
        "requestId": request_id,
    }
    if target_client_id:
        request_payload["targetClientId"] = target_client_id

    try:
        async with websockets.connect(ws_url, ping_interval=None) as websocket:
            await websocket.send(json.dumps({"type": "register", "role": "backend"}))
            await websocket.send(json.dumps(request_payload))

            while True:
                raw_message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError:
                    continue

                message_type = message.get("type")
                message_request_id = message.get("requestId")

                if message_type == "dom_snapshot_response" and message_request_id in {
                    None,
                    request_id,
                }:
                    if message.get("error"):
                        raise RuntimeError(message["error"])
                    return message

                if message_type == "dom_snapshot_error" and message_request_id in {
                    None,
                    request_id,
                }:
                    raise RuntimeError(message.get("error") or "DOM snapshot error")

                # Ignore status/register ack messages and continue waiting.
    except asyncio.TimeoutError as exc:
        raise RuntimeError(
            f"Timed out waiting for DOM snapshot response after {timeout} seconds"
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"Unable to connect to DOM snapshot websocket at {ws_url}: {exc}"
        ) from exc


@app.get("/dom-snapshot")
async def dom_snapshot(
    target_client_id: Optional[str] = None,
    ws_url: Optional[str] = None,
    timeout: Optional[float] = None,
):
    """
    Connect to the frontend websocket bridge and return a DOM snapshot.

    Query parameters:
    - target_client_id: optional websocket client id when multiple frontends are connected.
    - ws_url: override websocket endpoint url.
    - timeout: override request timeout (seconds).
    """
    resolved_ws_url = ws_url or DOM_SNAPSHOT_WS_URL_DEFAULT
    resolved_timeout = timeout or DOM_SNAPSHOT_REQUEST_TIMEOUT_DEFAULT

    try:
        snapshot = await fetch_dom_snapshot(
            ws_url=resolved_ws_url,
            timeout=resolved_timeout,
            target_client_id=target_client_id,
        )
        return snapshot
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "executor.server:app",
        host=EXECUTOR_SERVER_HOST,
        port=EXECUTOR_SERVER_PORT,
        reload=bool(os.getenv("EXECUTOR_SERVER_RELOAD", "")),
    )
