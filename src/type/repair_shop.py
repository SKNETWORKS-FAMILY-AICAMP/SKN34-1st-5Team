from dataclasses import dataclass
from src.type.location import Location
from src.type.repair_shop_type import RepairShopType

@dataclass
class RepairShop(Location):
    """정비소의 타입을 구분하는 데이터 클래스
    Attributes:
      repair_shop_type: 정비소 타입을 구분하는 항목
      repair_scope: 정비소 범위를 나타내는 항목
    """
    repair_shop_type : RepairShopType
    repair_scope : str