"""지역별 전기차 통계 데이터 모듈"""


from src.type.region import Region

class RegionEVStats:
    """지역별 전기차 등록 통계 데이터 클래스"""

# 생성자 
    def __init__(
            self,
            electric_vehicle_count: int,
            population: int,
            region: Region,
            year: int,
            base_date: str,
    ):
        
        self.electric_vehicle_count: int = electric_vehicle_count
        """해당 지역의 전기차 등록대수"""

        self.population: int = population
        """해당 지역의 인구수"""

        self.region: Region = region
        """해당 전기차 등록 지역"""

        self.year: int = year
        """통계 기준 연도"""

        self.base_date : str = base_date
        """통계 기준일"""