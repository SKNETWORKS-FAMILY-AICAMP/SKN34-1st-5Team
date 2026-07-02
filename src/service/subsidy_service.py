"""보조금 서비스"""

import csv
import os

from src.repository.repository import Repository
from src.type.electric_vehicle import ElectricVehicle
from src.type.region import Region
from src.type.subsidy import Subsidy
from src.util.region_mapper import str_to_region


def get_subsidy(region: Region, vehicle: ElectricVehicle) -> Subsidy | None:
    """
    Args:
        region: 보조금을 조회할 지역 정보
        vehicle: 보조금을 조회할 전기차 차량 정보

    Returns:
        지역과 차량 기준으로 조회된 Subsidy 객체
    """

    db = Repository()

    subsidy: Subsidy | None = db.find_subsidy(
        region=region,
        vehicle=vehicle
    )

    return subsidy


def set_subsidy(file_path: str) -> None:
    """
    Args:
        file_path: 적재할 보조금 CSV 파일 경로

    Returns:
        없음
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {file_path}")

    db = Repository()

    vehicles: list[ElectricVehicle] = db.find_all_vehicle()

    with open(file_path, encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            electric_vehicle: ElectricVehicle | None = None

            for vehicle in vehicles:
                if vehicle.model_name == row["모델명"]:
                    electric_vehicle = vehicle
                    break

            if electric_vehicle is None:
                print(f"차량 없음 - 건너뜀: {row['제조사']} / {row['모델명']}")
                continue

            subsidy = Subsidy(
                year=int(row["연도"]),
                region=str_to_region(row["지역"]),
                electric_vehicle=electric_vehicle,
                national_subsidy=int(row["국비"]),
                local_subsidy=int(row["지방비"]),
                national_conversion_subsidy=int(row["전환지원금_국비"]),
                local_conversion_subsidy=int(row["전환지원금_지방비"]),
            )
            db.create_subsidy(subsidy=subsidy)