#from scipy import interpolate
from datetime import datetime
from time import time
from logger import log_info

class BoatParameters:
    previous_boat_parameters = None
    timestamp = 0
    distance = 0
    speed = 0
    time = 0

    def __init__(self, time_ms, speed_mm_sec, distance_mm, prev = None, extrapolated = False, timestamp=None):
        self.timestamp = self.current_milliseconds() if timestamp is None else timestamp
        self.distance = distance_mm
        self.speed = speed_mm_sec
        self.time = time_ms 
        self.previous_boat_parameters = prev
        self.is_extrapolated = extrapolated
    #    if prev:
    #        log_info(f"dtstamp: {self.timestamp - prev.timestamp}, dt: {self.time - prev.time}, ds: {self.speed - prev.speed}, dd: {self.distance - prev.distance}, ex: {self.is_extrapolated}")

    def get_next(self, time_ms, speed_mm_sec, distance_mm, prev):
        return BoatParameters(time_ms, speed_mm_sec, distance_mm, prev)

    def get_next_for_now(self):
        self.get_next_for_timestamp(self.current_milliseconds())

    def get_next_for_timestamp(self, timestamp):
        speed = 0
        dt = timestamp - self.timestamp
        if dt <= 1:
            return self
        if self.previous_boat_parameters:
            dti = self.time - self.previous_boat_parameters.time
            if dti <= 0:
                return self
            acceleration = (self.speed / 1000 - self.previous_boat_parameters.speed / 1000) / dti
            speed = self.speed / 1000 + acceleration * dt
        else:
            speed = self.speed / 1000
        distance = self.distance + int(speed * dt)
        return BoatParameters(self.time + dt, int(speed*1000), (distance), prev = self, extrapolated = True, timestamp=timestamp)

    def current_milliseconds(self):
        dt = datetime.now()
        ts = dt.timestamp()
        return int((ts / 100 - int(ts / 100)) * 100000)

if __name__ == '__main__':
    #dataset = [[15999, 4294, 36919, 33259], [16049,4269,37103,33306],[33350],[33351],[33351],[33352],[33352],[33353], [16100, 4243,37287, 33361]]
    dataset = [[15999,2247,26193,46436],[46446],[46456],[46467],[46477],[16049, 2240, 26291,46487]]

    bp = []
    for item in dataset:
        if len(item) == 4:
            bp.append(BoatParameters(time_ms=item[0], speed_mm_sec=item[1], distance_mm=item[2],timestamp=item[3], prev=bp[-1] if len(bp) > 0 else None))
        else:
            bp.append(bp[-1].get_next_for_timestamp(item[0]))

    for item in bp:
        print(item.time, item.speed, item.distance)

if __name__ == '__maijn__':
    bp = []
    #2024-02-02 23:27:38,616 - logger - INFO - udp: 21350 3633 57269
    bp.append(BoatParameters(time_ms=21350, speed_mm_sec=3633, distance_mm=57269, timestamp=38616))
    #2024-02-02 23:27:38,636 - logger - INFO - Get Response 
    bp.append(bp[-1].get_next_for_timestamp(38636))
    #2024-02-02 23:27:38,637 - logger - INFO - Get Response 
    bp.append(bp[-1].get_next_for_timestamp(38637))
    #2024-02-02 23:27:38,638 - logger - INFO - Get Response 
    bp.append(bp[-1].get_next_for_timestamp(38638))
    #2024-02-02 23:27:38,666 - logger - INFO - udp: 21399 3645 57427
    bp.append(BoatParameters(time_ms=21399, speed_mm_sec=3645, distance_mm=57427, timestamp=38666))
  #  time.sleep(0.007)
    
    for item in bp:
        print(item.time, item.speed, item.distance)
