import sys
import asyncio
import websockets
from loguru import logger
import json
from typing import Callable
from bot.config import settings

# WebSocket server URL for logs
WS_SERVER_URL = "ws://localhost:3000/ws"  # Update this to your server's URL if needed

# Determine the logging level based on settings
level = "DEBUG" if settings.DEBUG else "INFO"

# Async function to send logs to the server
async def send_log_to_server(log_data):
    async with websockets.connect(WS_SERVER_URL) as websocket:
        await websocket.send(log_data)

# Log handler for WebSocket
async def log_handler(message):
    log_data = {
        "time": message.record["time"].timestamp(),
        "level": message.record["level"].name,
        "message": message.record["message"],
        "botName": "Blum"
    }
    await send_log_to_server(json.dumps(log_data))

# Configure loguru logger
logger.remove()
logger.add(sink=sys.stdout, level=level, format="<light-white>{time:YYYY-MM-DD HH:mm:ss}</light-white>"
                                               " | <level>{level}</level>"
                                               " | <light-white><b>{message}</b></light-white>")
logger.add("blum_dev.log", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", rotation="20 MB")
logger.add(log_handler, format="{time} {level} {message}", serialize=True)
logger = logger.opt(colors=True)

# Utility functions for logging
def info(text):
    return logger.info(text)

def debug(text):
    return logger.debug(text)

def warning(text):
    return logger.warning(text)

def error(text):
    return logger.error(text)

def critical(text):
    return logger.critical(text)

def success(text):
    return logger.success(text)

# Method to disable color formatting on error
def disable_color_on_error(formatter, level_):
    def wrapper(*args, **kwargs):
        try:
            getattr(logger, level_)(formatter(*args, **kwargs))
        except ValueError:
            getattr(logger.opt(colors=False), level_)(*args, **kwargs)
    return wrapper

# SessionLogger class for customized logging per session
class SessionLogger:
    session_name: str
    trace: Callable[[str], None]
    debug: Callable[[str], None]
    info: Callable[[str], None]
    success: Callable[[str], None]
    warning: Callable[[str], None]
    error: Callable[[str], None]
    critical: Callable[[str], None]

    def __init__(self, session_name):
        self.session_name = session_name
        for method_name in ("trace", "debug", "info", "success", "warning", "error", "critical"):
            setattr(self, method_name, disable_color_on_error(self._format, method_name))

    def _format(self, message):
        return f"{self.session_name} | {message}"
