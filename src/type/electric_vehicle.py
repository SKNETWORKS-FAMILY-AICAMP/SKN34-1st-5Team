from src.type.manufacturer import Manufacturer
from src.type.charging_type import ChargingType

class ElectricVehicle:

    def __init__(
            self,
            manufacturer: Manufacturer,
            model_name: str,
            trim_name: str,
            price: int,
            driving_range: int,
            efficiency: float,
            slow_charging_type: ChargingType,
            fast_charging_type: ChargingType
            ):
        self.manufacturer: Manufacturer = manufacturer
        self.model_name: str = model_name
        self.trim_name: str = trim_name
        self.price: int = price
        self.driving_range: int = driving_range
        self.efficiency: float = efficiency
        self.slow_charging_type: ChargingType = slow_charging_type
        self.fast_charging_type: ChargingType = fast_charging_type