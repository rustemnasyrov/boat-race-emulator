import time


class TimeMeter :

    def __init__(self):
        self.start_time = time.time()
        self.last_time = self.start_time
        self.dt = 0

    def get_measure_str(self):
        self.current_time = int((time.time() - self.start_time) * 1000)  # Time since start in milliseconds
        self.dt = self.current_time - self.last_time
        return (str(self.current_time) + ' (' + str(self.dt) + ')')

    def update_time(self):
        self.last_time = self.current_time