"""전기차 차량 서비스"""

from src.repository.repository import Repository
from src.type.electric_vehicle import ElectricVehicle
from src.type.manufacturer import Manufacturer



def get_all() -> list[ElectricVehicle]:
    """
    Returns:
        전체 전기차 차량 목록
    """

    db = Repository()

    vehicles: list[ElectricVehicle] = db.find_all_electric_vehicles()

    return vehicles


def get_by_vehicle(model_name: str, trim_name: str) -> ElectricVehicle | None:
    """
    Args:
        model_name: 차량 모델명
        trim_name: 차량 트림명

    Returns:
        모델명과 트림명에 해당하는 ElectricVehicle 객체
    """

    db = Repository()

    vehicle: ElectricVehicle | None = db.find_electric_vehicle(
        model_name=model_name,
        trim_name=trim_name
    )

    return vehicle


def set_vehicle(vehicle: ElectricVehicle) -> None:
    """
    Args:
        vehicle: 등록할 ElectricVehicle 객체

    Returns:
        없음
    """

    db = Repository()

    db.create_electric_vehicle(vehicle=vehicle)


def get_manufacturer() -> list[Manufacturer]:
    """
    Returns:
        제조사 Enum 목록
    """

    db = Repository()

    manufacturers: list[Manufacturer] = db.find_manufacturer()

    return manufacturers