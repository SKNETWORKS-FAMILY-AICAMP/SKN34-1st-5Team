
""" 지역 정보"""

from enum import Enum

class Region(Enum):
        """자동차 지역을 나타내는 열거형 클래스.
        
        차종 정보, FAQ 등 지역별 데이터를 다룰 때 문자열을 직접 사용하는
        대신 이 Enum을 사용하여 오타나 표기 불일치를 방지한다.
       
        """

        SEOUL = "서울"
        """서울"""
        BUSAN = "부산"
        """부산"""
        DAEGU = "대구"
        """대구"""
        INCHEON = "인천"
        """인천"""
        GWANGJU = "광주"
        """광주"""
        DAEJEON = "대전"
        """대전"""
        ULSAN = "울산"
        """울산"""
        SEJONG = "세종"
        """세종"""
        GYEONGGI = "경기"
        """경기"""
        GANGWON = "강원"
        """강원"""
        CHUNGBUK = "충북"
        """충북"""
        CHUNGNAM = "충남"
        """충남"""
        JEONBUK = "전북"
        """전북"""
        JEONNAM = "전남"
        """전남"""
        GYEONGBUK = "경북"
        """경북"""
        GYEONGNAM = "경남"
        """경남"""
        JEJU = "제주"
        """제주"""