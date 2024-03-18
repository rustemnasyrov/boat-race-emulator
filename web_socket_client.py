import asyncio
import websockets
import json
import time
      
from TimeMeter import TimeMeter

async def send_websocket():

    tm = TimeMeter()
    async with websockets.connect('ws://192.168.1.133:81') as websocket:
        while True:

            
            data = tm.get_measure_str()
            await websocket.send(data)
            await asyncio.sleep(0.025)
            tm.update_time()

asyncio.get_event_loop().run_until_complete(send_websocket())
