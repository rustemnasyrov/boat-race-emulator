import asyncio
import websockets
import json

async def send_websocket():
    async with websockets.connect('ws://localhost:8765') as websocket:
        while True:
            data = {"message": "Hello, world!"}
            await websocket.send(json.dumps(data))
            await asyncio.sleep(5)

asyncio.get_event_loop().run_until_complete(send_websocket())
