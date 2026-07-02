"""FAQ"""

import csv

from src.type.faq_item import FAQItem
from src.type.manufacturer import Manufacturer
from src.type.page import Page
from src.repository.repository import Repository


# 제조사 표기 -> Manufacturer Enum 값("현대", "기아") 매핑
# 매핑 파일 확인해보고 교체
MANUFATURER_NAME_MAP = {
    "현대자동차":"현대",
    "기아자동차":"기아",
}

def map_manufacturer_name(raw_name: str) -> str:
    return MANUFATURER_NAME_MAP.get(raw_name, raw_name)



def get_faq(page: int, size: int, manufacturer: Manufacturer) -> Page:
    """
    Args:
        page: 조회할 페이지 번호
        size: 한 페이지에서 가져올 FAQ개수
        manufacturer: 조회 대상 제조사
        
    Returns:
        조회된 FAQ 목록과 페이지 정보를 담은 Page 객체
    """

    db = Repository()
    

    category = manufacturer.value
    sub_category = page
    

    faq_items: list[FAQItem] = db.find_faq(category=category, sub_category=sub_category)


    total_count = len(faq_items)
    total_page = (total_count + size -1) // size if size > 0 else 0

    start = (page -1) * size
    end = start + size
    paged_items = faq_items[start:end]

    return Page(
        item = paged_items,
        total_page = total_page,
        current_page = page
    )

def set_faq(file_path: str) -> None:
    """
    Args:
        file_path: 적재할 FAQ CSV 파일의 경로.

    Returns:
        없음.
    """

    db = Repository()

    with open(file_path, encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            raw_company = row["company"]
            manufacturer_name = MANUFATURER_NAME_MAP.get(raw_company, raw_company)

            faq_item = FAQItem(
                manufacturer=Manufacturer(manufacturer_name),
                category=row["category"],
                question=row["question"],
                answer=row["answer"],
                source_url=row["source_url"],
            )
            db.create_faq(faq_item)


