class BoatJsonInjection:

    def to_json(self):
        return self.__dict__.copy()
    
    @classmethod
    def from_json(cls, json_data):
        result = cls()
        for key in result.__dict__.keys():
            if key in json_data:
                result.__dict__[key] = json_data[key]

        return result