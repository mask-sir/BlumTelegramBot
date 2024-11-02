import asyncio
from aiohttp import web, WSMsgType
import json
from datetime import datetime

# Store WebSocket connections and logs
ws_connections = set()
stored_logs = []
MAX_STORED_LOGS = 1000  # Adjust this value to change the number of logs to keep in memory

async def handle(request):
    with open('index.html', 'r') as f:
        html_content = f.read()
    return web.Response(text=html_content, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    ws_connections.add(ws)
    
    # Send stored logs to the new connection
    for log in stored_logs:
        await ws.send_str(json.dumps(log))
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    log_data = json.loads(msg.data)
                    log_entry = {
                        "record": {
                            "time": {
                                "timestamp": str(log_data['time'])
                            },
                            "level": {
                                "name": log_data['level']
                            },
                            "message": log_data['message'],
                            "botName": log_data['botName']
                        }
                    }
                    stored_logs.append(log_entry)
                    if len(stored_logs) > MAX_STORED_LOGS:
                        stored_logs.pop(0)
                    await broadcast_log(log_entry)
                except json.JSONDecodeError:
                    print("Invalid JSON received")
            elif msg.type == WSMsgType.ERROR:
                print(f'WebSocket connection closed with exception {ws.exception()}')
    finally:
        ws_connections.remove(ws)
    
    return ws

async def broadcast_log(message):
    closed_ws = set()
    for ws in ws_connections:
        try:
            await ws.send_str(json.dumps(message))
        except ConnectionResetError:
            closed_ws.add(ws)
    
    ws_connections.difference_update(closed_ws)

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/ws', websocket_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("Server started at http://0.0.0.0:3000")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(run_web_server())
