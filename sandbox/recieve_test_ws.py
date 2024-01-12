import asyncio
import websockets

async def read_websocket():
    async with websockets.connect('ws://localhost:8765') as websocket:
        while True:
            message = await websocket.recv()
            print(message)

asyncio.get_event_loop().run_until_complete(read_websocket())
