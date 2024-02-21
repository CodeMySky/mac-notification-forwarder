import asyncio
import logging
import logging.handlers as handlers
import os

from fastapi import FastAPI, Request, Response, WebSocket
from fastapi_utils.tasks import repeat_every
import uvicorn
import yaml

from mnf.notification_monitor import MacNotificationMonitor


logger = logging.getLogger(__name__)
app = FastAPI()
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)


@repeat_every(seconds=1)
async def check_notification() -> None:
    monitor = MacNotificationMonitor.get_monitor()
    monitor.check_system_notifications()


@app.on_event("startup")
async def startup_event():

    logging_level: str = config.get("sys", {}).get("logging_level", "INFO")
    logging.getLogger().setLevel(logging_level)
    logging_file: str = config.get("sys", {}).get("logging_file", "history.log")
    try:
        os.remove(logging_file)
    except FileNotFoundError:
        pass
    logging.getLogger().addHandler(
        handlers.RotatingFileHandler(logging_file, mode="a", maxBytes=1024)
    )

    await check_notification()


async def log_reader(n=5):
    log_lines = []
    logging_file = config.get("sys", {}).get("logging_file", "history.log")
    with open(logging_file, "r") as file:
        for line in file.readlines()[-n:]:
            log_lines.append(f"{line}<br/>")
        return log_lines


@app.websocket("/ws/log")
async def websocket_endpoint_log(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await asyncio.sleep(1)
            logs = await log_reader(30)
            await websocket.send_text(logs)
    except Exception as e:
        logger.error(e)
    finally:
        await websocket.close()


@app.get("/")
async def get(request: Request):
    html_content = """
    <html>
    <body>
    <div id="logs">Logs</div>
    <script>
    var ws_log = new WebSocket("ws://localhost:8000/ws/log");

    ws_log.onmessage = function (event) {
        var logs = document.getElementById("logs");
        var log_data = event.data;
        logs.innerHTML = log_data;
    };
    </script>
    </body>
    </html>
    """
    return Response(
        content=html_content,
        media_type="text/html",
    )


if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="localhost",
        port=8000,
        workers=1,
    )
