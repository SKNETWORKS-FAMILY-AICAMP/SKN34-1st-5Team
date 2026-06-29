"""제조사 정보를 표준화하여 관리하는 모듈"""

from enum import Enum

class Manufacturer(Enum):
    """자동차 제조사를 나타내는 열거형 클래스.
    
    차종 정보, FAQ 등 제조사별 데이터를 다룰 때 문자열을 직접 사용하는
    대신 이 Enum을 사용하여 오타나 표기 불일치를 방지한다.
    
    Attributes:
        HYUNDAI: 현대자동차를 나타내는 값.
        KIA: 기아를 나타내는 값.
    """

    HYUNDAI = "현대"
    """현대자동차"""

    KIA = "기아"
    """기아"""