from src.type.region import Region
from src.type.electric_vehicle import ElectricVehicle

class Subsidy:
    def __init__(
            self,
            year: int,
            region: Region,
            electric_vehicle: ElectricVehicle,
            national_subsidy: int,
            local_subsidy: int,
            national_conversion_subsidy: int = 0,
            local_conversion_subsidy: int = 0
            ):
        self.year: int = year
        self.region: Region = region
        self.electric_vehicle: ElectricVehicle = electric_vehicle
        self.national_subsidy: int = national_subsidy
        self.local_subsidy: int = local_subsidy
        self.national_conversion_subsidy: int = national_conversion_subsidy
        self.local_conversion_subsidy: int = local_conversion_subsidy

    def get_total_support_amount(self) -> int:
        return self.national_subsidy + self.local_subsidy
    
    def get_total_subsidy(self) -> int:
        return self.national_conversion_subsidy + self.local_conversion_subsidy
        