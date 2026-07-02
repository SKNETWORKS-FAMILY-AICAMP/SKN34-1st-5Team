-- EV Purchase Support Information System Enum Seed Data
-- 파이썬 Enum 클래스(Manufacturer, ChargingType, Region, RepairShopType)에 정의된
-- 값들을 그대로 대응하는 룩업 테이블에 적재한다.
-- code 컬럼이 필요한 테이블(region, repair_shop_type)은 Enum의 멤버 이름(.name)을 code로 쓴다.

-- 1. Manufacturer (src/type/manufacturer.py)

INSERT INTO manufacturer (name) VALUES
    ('현대'),
    ('기아'),
    ('제네시스');


-- 2. ChargingType (src/type/charging_type.py)

INSERT INTO charging_type (name) VALUES
    ('AC_단상_5핀'),
    ('DC_콤보_1'),
    ('차데모'),
    ('AC_3상_7핀');


-- 3. Region (src/type/region.py)

INSERT INTO region (code, name) VALUES
    ('SEOUL', '서울'),
    ('BUSAN', '부산'),
    ('DAEGU', '대구'),
    ('INCHEON', '인천'),
    ('GWANGJU', '광주'),
    ('DAEJEON', '대전'),
    ('ULSAN', '울산'),
    ('SEJONG', '세종'),
    ('GYEONGGI', '경기'),
    ('GANGWON', '강원'),
    ('CHUNGBUK', '충북'),
    ('CHUNGNAM', '충남'),
    ('JEONBUK', '전북'),
    ('JEONNAM', '전남'),
    ('GYEONGBUK', '경북'),
    ('GYEONGNAM', '경남'),
    ('JEJU', '제주');


-- 4. RepairShopType (src/type/repair_shop_type.py)

INSERT INTO repair_shop_type (code, name) VALUES
    ('HYUNDAI_BLUEHANDS', '블루핸즈'),
    ('KIA_AUOT_Q', '기아 오토큐');
