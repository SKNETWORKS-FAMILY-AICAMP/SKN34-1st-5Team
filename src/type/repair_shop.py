from dataclasses import dataclass

@dataclass
class RepairShop(Location):
    """정비소의 타입을 구분하는 데이터 클래스
    Attributes:
      repair_shop_type: 정비소 타입을 구분하는 항목
    """
    repair_shop_type : RepairShopType