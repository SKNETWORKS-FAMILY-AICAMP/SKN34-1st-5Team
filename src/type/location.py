from dataclasses import dataclass

@dataclass
class Location:
    """이름, 지역, 시/군/구, 주소, 위도, 경도, 이용 가능 시간,
    연락처 정보를 담는 공통 위치 데이터 클래스
    Attributes:
     name: 이름 정보가 담긴 항목
     region: 지역 정보가 담긴 항목
     city: 시/군/구 정보가 담긴 항목
     address: 주소 정보가 담긴 항목
     latitude: 위도 정보가 담긴 항목
     longitude: 경도 정보가 담긴 항목
     available_time: 이용 가능 시간 정보가 담긴 항목
     contact: 연락처 정보가 담긴 항목
    """
    name: str
    '''이름 정보가 담긴 항목'''
    region: Reigon
    '''지역 정보가 담긴 항목'''
    city: str
    '''시/군/구 정보가 담긴 항목'''
    address: str
    '''주소 정보가 담긴 항목'''
    latitude: float
    '''위도 정보가 담긴 항목'''
    longitude: float
    '''경도 정보가 담긴 항목'''
    available_time: str
    '''이용 가능 시간 정보가 담긴 항목'''
    contact: str
    '''연락처 정보가 담긴 항목'''

