from src.type.manufacturer import Manufacturer
from src.type.electric_vehicle import ElectricVehicle

class Subsidy:
    def __init__(self):
        self.year: int
        self.region: Region
        self.electric_vehicle: ElectricVehicle()
        self.national_subsidy: int
        self.local_subsidy: int
        self.national_conversion_subsidy: int
        self.local_conversion_subsidy: int
    def get_total_support_amount(self) -> int:
        return self.national_subsidy + self.local_subsidy
    def get_total_subsidy(self) -> int:
        return self.national_conversion_subsidy + self.local_conversion_subsidy
        