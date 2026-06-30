from src.type.manufacturer import Manufacturer

class ElectricVehicle:

    def __init__(self):
        self.manufacturer = Manufacturer()
        self.model_name: str
        self.trim_name: str
        self.price: int
        self.driving_range: int
        self.efficiency: float
        self.slow_charging_type: ChargingType
        self.fast_charging_type: ChargingType

