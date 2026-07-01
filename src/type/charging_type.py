"""충전기 종류"""

from enum import Enum

class ChargingType(Enum):
    """
    충전기 종류를 나타내는 열거형 클래스.
    차종 정보, FAQ 등 충전기 종류별 데이터를 다룰 때 문자열을 직접 사용하는
    대신 이 Enum을 사용하여 오타나 표기 불일치를 방지한다.
    """

    AC_SINGLE_PHASE_5_PIN = "AC_단상_5핀"
    """AC_단상_5핀_충전"""

    DC_COMBO_1 = "DC_콤보_1"
    """DC_콤보_1_충전"""

    CHADEMO = "차데모"
    """차데모 충전"""

    AC_THREE_PHASE_7_PIN = "AC_3상_7핀"
    """AC_3상_7핀_충전"""