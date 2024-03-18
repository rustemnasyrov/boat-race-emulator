import asyncio
import websockets

from TimeMeter import TimeMeter

tm = TimeMeter()
        
async def echo(websocket, path):
    global tm
    async for message in websocket:
        print(message + ' --> ' + tm.get_measure_str() )
        tm.update_time()

async def start_server():
    server = await websockets.serve(echo, "192.168.1.133", 81)
    await server.wait_closed()

async def main():
    asyncio.set_event_loop(asyncio.new_event_loop())  # Set up a new event loop
    await start_server()

if __name__ == "__main__":
    asyncio.run(main())