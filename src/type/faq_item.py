"""FAQ 항목 데이터를 표현하는 모듈"""

from dataclasses import dataclass

from src.type.manufacturer import Manufacturer

@dataclass
class FAQItem:
    """FAQ 항목 하나를 표현하는 데이터 클래스

    크롤링으로 수집한 자동차 기업의 FAQ 데이터를 담는 그릇 역할을 한다

    Attributes:
        manufacturer: 해당 FAQ가 속한 제조사
        category: FAQ의 분류(카테고리)
        question: FAQ 질문내용
        answer: FAQ 답변 내용
        source_url: 해당 FAQ를 수집한 원본 페이지 URL
    """

    manufacturer: Manufacturer
    """해당 FAQ가 속한 제조사"""

    category: str
    """FAQ 질문내용"""

    question: str
    """FAQ 질문 내용"""

    answer: str
    """FAQ 답변 내용"""

    source_url: str
    """해당 FAQ를 수집한 원본 페이지 URL"""