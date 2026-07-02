
"""전기차 차량 서비스"""


from src.repository.repository import Repository
from src.type.electric_vehicle import ElectricVehicle
from src.type.manufacturer import Manufacturer


def get_all() -> list[ElectricVehicle]:
    """
    DB에 저장된 전체 전기차 차량 목록을 조회한다.

    Returns:
        list[ElectricVehicle]: 전체 전기차 차량 목록
    """

    db = Repository()

    vehicles: list[ElectricVehicle] = db.find_all_vehicle()

    return vehicles


def get_by_vehicle(
    model_name: str,
    trim_name: str
) -> ElectricVehicle | None:
    """
    모델명과 트림명을 기준으로 특정 전기차 차량 정보를 조회한다.

    Args:
        model_name: 차량 모델명
        trim_name: 차량 트림명

    Returns:
        ElectricVehicle | None: 조회된 전기차 차량 정보
    """

    db = Repository()

    vehicle: ElectricVehicle | None = db.find_all_vehicle(
        model_name=model_name,
        trim_name=trim_name
    )

    return vehicle


def set_vehicle(vehicle: ElectricVehicle) -> None:
    """
    전기차 차량 정보를 DB에 등록한다.

    Args:
        vehicle: 등록할 ElectricVehicle 객체

    Returns:
        없음
    """

    db = Repository()

    db.create_vehicle(vehicle=vehicle)


def get_manufacturer() -> list[Manufacturer]:
    """
    등록된 제조사 목록을 조회한다.

    Returns:
        list[Manufacturer]: 제조사 목록
    """

    db = Repository()

    manufacturers: list[Manufacturer] = db.find_all_manufacturers()

    return manufacturers