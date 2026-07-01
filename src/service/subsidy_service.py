"""Subsidy 서비스 클래스 생성"""


from src.type.region import Region
from src.type.electric_vehicle import ElectricVehicle
from src.type.subsidy import Subsidy
from src.repository.repository import Repository


class SubsidyService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SubsidyService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.repository = Repository()

    def get_subsidy(
        self,
        region: Region,
        electric_vehicle: ElectricVehicle
    ) -> Subsidy | None:
        """
        지역과 전기차 정보를 기준으로 보조금 정보를 조회한다.
        """
        subsidy = self.repository.find_subsidy_by_region_and_vehicle(
            region,
            electric_vehicle
        )

        return subsidy

    def set_subsidy(self, file_path: str) -> None:
        """
        파일 경로를 받아 보조금 데이터를 등록한다.
        """
        self.repository.save_subsidy_from_file(file_path)