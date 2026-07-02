
"""지역별 전기차 통계 데이터 조회 및 적재 서비스 모듈"""

import csv
import os

from src.repository.repository import Repository
from src.type.region import Region
from src.type.region_EV_stats import RegionEVStats



# Singleton 구조로 작성하여 서비스 객체가 여러 번 생성되지 않도록 
class StatisticsService:
    _instance = None                              # 만들어진 객체 여기 보관 

    def __new__(cls):
        if cls._instance is None:                  
            cls._instance = super().__new__(cls)    
        return cls._instance                        



    # 시도별 전기차 등록대수
    def get_ev_registration_by_region(self, year:int, region:Region = None) -> RegionEVStats:
      """
       
      Args:
          year: 조회할 기준 연도. None이면 전체 연도 기준으로 조회한다
          region: 조회할 지역. 반드시 입력 !!
            
      Returns:
          해당 지역과 연도 기준의 전기차 등록대수 통계 정보
            
      Raises:
          ValueError: region이 None인 경우
      """
       
      if region is None:
        raise ValueError("region은 필수로 입력값입니다")
        
      repository = Repository()

      return repository.find_ev_count_by_region(region=region)
    


    # 인구대비 전기차 보유율
    def get_ev_adoption_rate_by_population(self, year: int, region : Region = None) -> RegionEVStats:
       
       # args, return, raises 동일

       if region is None:
          raise ValueError("region은 필수로 입력값입니다")
       
       
       repository = Repository()
       return repository.find_population_by_region(region=region)
    

    
    # 시도별 전기차 등록대수 파일읽고 db에 적재하기 
    def set_ev_registration_by_region(self, file_path: str):


      # 파일 존재 여부 확인
      if not os.path.exists(file_path):
         raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
      repository = Repository()
    

      # 파일 읽고 DB에 저장
      with open(file_path, encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)                         # 딕셔너리 형태로 읽어주기
        for row in reader:
           region = Region(row["지역"])
           year = int(row['연도'])
           electric_vehicle_count = int(row["전기차등록대수"])

           stats = RegionEVStats(
              electric_vehicle_count = electric_vehicle_count,
              population = 0,
              region = region,
              year = year,
              base_date = str(year),
           )

           repository.create_ev_count_by_region(stats)




    # 인구대비 전기차 보유율 파일읽고 db에 적재하기 
    def set_ev_adoption_rate_by_population(self, file_path:str):
       
      # 파일 존재 여부 확인
      if not os.path.exists(file_path):
         raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
      repository = Repository()
    

      # 파일 읽고 DB에 저장
      with open(file_path, encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)                         # 딕셔너리 형태로 읽어주기
        for row in reader:
           region = Region(row["지역"])
           year = int(row['연도'])
           electric_vehicle_count = int(row["전기차등록대수"])
           population = int(row["인구수"])


           stats = RegionEVStats(
              electric_vehicle_count = electric_vehicle_count,
              population = population,
              region = region,
              year = year,
              base_date = str(year),
           )

           repository.create_population_by_region(stats)
