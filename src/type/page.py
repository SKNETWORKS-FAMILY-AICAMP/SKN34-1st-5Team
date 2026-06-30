""" 페이지 결과 표현하는 모듈"""


from dataclasses import dataclass
from typing import Any

@dataclass
class Page:
   """페이지 단위로 조회된 결과를 표현하는 데이터 클래스
   Attributes:
    item: 현재 페이지에 포함된 항목 목록
    total_page: 전체 페이지 수
    current_page: 현재 페이지 번호
   """

   
   item: list[Any]
   """현재 페이지에 포함된 항목 목록"""

   total_page: int
   """전체 페이지수"""

   current_page: int
   """현재 페이지 번호"""





