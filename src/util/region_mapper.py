"""지역명과 Region Enum 매핑 유틸"""

from src.type.region import Region


REGION_NAME_TO_ENUM: dict[str, Region] = {
    "서울특별시": Region.SEOUL,
    "부산광역시": Region.BUSAN,
    "대구광역시": Region.DAEGU,
    "인천광역시": Region.INCHEON,
    "광주광역시": Region.GWANGJU,
    "대전광역시": Region.DAEJEON,
    "울산광역시": Region.ULSAN,
    "세종특별자치시": Region.SEJONG,
    "경기도": Region.GYEONGGI,
    "강원특별자치도": Region.GANGWON,
    "충청북도": Region.CHUNGBUK,
    "충청남도": Region.CHUNGNAM,
    "전북특별자치도": Region.JEONBUK,
    "전라남도": Region.JEONNAM,
    "경상북도": Region.GYEONGBUK,
    "경상남도": Region.GYEONGNAM,
    "제주특별자치도": Region.JEJU,
}


REGION_ENUM_TO_NAME: dict[Region, str] = {
    region: name
    for name, region in REGION_NAME_TO_ENUM.items()
}


def str_to_region(region_name: str) -> Region:
    """
    CSV 지역명 문자열을 Region Enum으로 변환한다.

    Args:
        region_name: CSV에 들어있는 지역명 문자열

    Returns:
        Region: 변환된 Region Enum
    """

    cleaned_region_name = region_name.strip()

    if cleaned_region_name not in REGION_NAME_TO_ENUM:
        raise ValueError(f"알 수 없는 지역명입니다: {region_name}")

    return REGION_NAME_TO_ENUM[cleaned_region_name]


def region_to_str(region: Region) -> str:
    """
    Region Enum을 지역명 문자열로 변환한다.

    Args:
        region: Region Enum 값

    Returns:
        str: 사람이 읽을 수 있는 지역명 문자열
    """

    if region not in REGION_ENUM_TO_NAME:
        raise ValueError(f"알 수 없는 Region Enum입니다: {region}")

    return REGION_ENUM_TO_NAME[region]