"""Subsidy 서비스 클래스 생성"""

import csv

from src.type.region import Region
from src.type.electric_vehicle import ElectricVehicle
from src.type.subsidy import Subsidy
from src.repository.repository import Repository


def get_subsidy(
    
    region: Region,
    electric_vehicle: ElectricVehicle
    ) -> Subsidy:
    """
    지역과 전기차 정보를 기준으로 보조금 정보를 조회한다.
    """
    subsidy = Repository.find_subsidy_by_region_and_vehicle(
        region,
        electric_vehicle
    )

    return subsidy

def set_subsidy(file_path: str) -> None:
    """
    파일 경로를 받아 보조금 데이터를 등록한다.
    """
    Repository.save_subsidy_from_file(file_path)