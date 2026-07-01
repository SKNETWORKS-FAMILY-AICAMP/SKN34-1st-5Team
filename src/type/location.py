from dataclasses import dataclass

@dataclass
class Location:
    name: str
    region: Reigon
    city: str
    address: str
    latitude: float
    longitude: float
    available_time: str
    contact: str

