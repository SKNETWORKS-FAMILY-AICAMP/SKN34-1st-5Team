from src.type.manufacturer import Manufacturer
from src.type.charging_type import ChargingType

class ElectricVehicle:

    def __init__(
            self,
            model_name: str,
            trim_name: str,
            manufacturer: Manufacturer = None,
            price: int = None,
            driving_range: int = None,
            efficiency: float = None,
            slow_charging_type: ChargingType = None,
            fast_charging_type: ChargingType = None
            ):
        self.manufacturer: Manufacturer = manufacturer
        self.model_name: str = model_name
        self.trim_name: str = trim_name
        self.price: int = price
        self.driving_range: int = driving_range
        self.efficiency: float = efficiency
        self.slow_charging_type: ChargingType = slow_charging_type
        self.fast_charging_type: ChargingType = fast_charging_type