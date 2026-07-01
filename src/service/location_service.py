import csv
import os

from src.type.page import Page
from src.type.location import Location
from src.type.repair_shop import RepairShop
from src.type.region import Region
from src.repository.repository import Repository



# 전기차 충전소 위치 조회

def get_charging_station_by_region(region:Region, city:str, page:int, size: int) -> Page:
    '''
    Args:
     region: 조회할 지역
     city: 조회할 시/군/구
     page: 조회할 페이지 번호
     size: 한 페이지에서 가져올 충전소 목록
    '''
    
    db = Repository()

    loc_info: list[Location] = db.find_charging_station(region, city)
    total_count = len(loc_info)
    total_page = (total_count + size -1) // size if size > 0 else 0
    start = (page -1) * size
    end = start + size
    paged_items = loc_info[start:end]



    
    return Page(
        item = paged_items,
        total_page = total_page,
        current_page = page

    )

# 정비소 위치 조회 

def get_repair_shop_by_region(region: Region, city: str, page:int, size:int) -> Page:
    
    db = Repository()

    rps: list[Location] = db.find_repair_shop(region, city)
    total_count = len(rps)
    total_page = (total_count + size -1) // size if size > 0 else 0
    start = (page -1) * size
    end = start + size
    paged_items = rps[start:end]

    return Page(
        item = paged_items,
        total_page = total_page,
        current_page = page
    )

# 충전소 위치 파일 읽고 DB에 저장하기

def set_charging_station_by_region(self, file_path: str) -> None:
    '''
    Args:
        file_path:적재할 csv파일 경로
    '''

    if not os.path.exists(file_path):
        raise print(f"파일이 존재하지 않습니다: {file_path}")
    
    repository = Repository()
    
    with open(file_path, encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            division = row["address"].split(" ", maxsplit = 1)
            
            location = Location(
                name = row["name"],
                region = row["region"],
                city = division[0],
                address = division[1],
                latitude = row["latitude"],
                longitude = row["longitude"],
                available_time = row["available_time"],
                contact = row["contact"]
            )
            repository.create_charging_station(location)

# 정비소 위치 파일 읽고 DB에 저장하기

def set_repair_shop_by_region(self, file_path: str) -> None:
    '''
    Args:
        file_path: 적재할 csv파일 경로
    '''
    if not os.path.exists(file_path):
        raise print(f"파일이 존재하지 않습니다: {file_path}")
    
    repository = Repository()

    with open(file_path, encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            division = row["address"].split(" ", maxsplit = 1)
            locate = RepairShop(
                name = row["name"],
                region = row["region"],
                city = division[0],
                address = division[1],
                latitude = row["latitude"],
                longitude = row["longitude"],
                repair_shop_type = row["repair_shop_type"],
                repair_scope = row["repair_scope"],
                available_time = row["available_time"],
                contact = row["contact"]
            )
            repository.create_repair_shop(locate)

# 시/군/구 정보 리스트로 얻기

def get_city(region: Region) -> list:
    
    db = Repository()

    gc: list[Location] = db.find_city(region)

    return gc





    