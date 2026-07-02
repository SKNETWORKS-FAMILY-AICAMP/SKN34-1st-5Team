"""충전타입과 ChargingType Enum 매핑 유틸"""

from src.type.charging_type import ChargingType


CHARGING_TYPE_NAME_TO_ENUM: dict[str, ChargingType] = {
    "AC 단상 5핀": ChargingType.AC_SINGLE_PHASE_5_PIN,
    "DC 콤보 1": ChargingType.DC_COMBO_1,
    "차데모": ChargingType.CHADEMO,
    "AC 3상 7핀": ChargingType.AC_THREE_PHASE_7_PIN,
}


CHARGING_TYPE_ENUM_TO_NAME: dict[ChargingType, str] = {
    charging_type: name
    for name, charging_type in CHARGING_TYPE_NAME_TO_ENUM.items()
}


def str_to_charging_type(charging_type_name: str) -> ChargingType:
    """
    CSV 충전타입 문자열을 ChargingType Enum으로 변환한다.

    Args:
        charging_type_name: CSV에 들어있는 충전타입 문자열

    Returns:
        ChargingType: 변환된 ChargingType Enum
    """

    cleaned_charging_type_name = charging_type_name.strip()

    if cleaned_charging_type_name not in CHARGING_TYPE_NAME_TO_ENUM:
        raise ValueError(f"알 수 없는 충전타입입니다: {charging_type_name}")

    return CHARGING_TYPE_NAME_TO_ENUM[cleaned_charging_type_name]


def charging_type_to_str(charging_type: ChargingType) -> str:
    """
    ChargingType Enum을 충전타입 문자열로 변환한다.

    Args:
        charging_type: ChargingType Enum 값

    Returns:
        str: 사람이 읽을 수 있는 충전타입 문자열
    """

    if charging_type not in CHARGING_TYPE_ENUM_TO_NAME:
        raise ValueError(f"알 수 없는 ChargingType Enum입니다: {charging_type}")

    return CHARGING_TYPE_ENUM_TO_NAME[charging_type]