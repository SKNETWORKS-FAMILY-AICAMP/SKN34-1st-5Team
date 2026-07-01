"""DB 접근을 담당하는 Repository 모듈"""

import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector.connection import MySQLConnection

from src.type.charging_station import ChargingStation
from src.type.charging_type import ChargingType
from src.type.electric_vehicle import ElectricVehicle
from src.type.faq_item import FAQItem
from src.type.manufacturer import Manufacturer
from src.type.region import Region
from src.type.region_EV_stats import RegionEVStats
from src.type.repair_shop import RepairShop
from src.type.subsidy import Subsidy

load_dotenv()


class Repository:
    """DB 접근을 관리하는 싱글톤 클래스.

    FAQ, 보조금, 전기차, 지역별 전기차 통계 데이터를 조회·생성하는
    메서드를 제공하며, 애플리케이션 전체에서 하나의 인스턴스만 유지한다.

    Attributes:
        connection: 재사용할 MySQL 연결 객체.
    """

    _instance = None
    connection: MySQLConnection

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def get_connection(self) -> MySQLConnection:
        """활성 MySQL 연결을 반환한다. 연결이 끊겼으면 재연결한다."""
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(os.getenv("MYSQL_PORT", "3306")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
            )
        return self.connection

    def find_faq(self, category: str, sub_category: int) -> list[FAQItem]:
        """제조사명으로 FAQ 목록을 조회한다.

        Args:
            category: 조회할 제조사명 (Manufacturer.value).
            sub_category: 페이지 번호 (현재 DB 필터링에는 사용하지 않음).

        Returns:
            조건에 맞는 FAQItem 목록.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM v_faq_full WHERE manufacturer_name = %s",
                (category,),
            )
            rows = cursor.fetchall()
            return [
                FAQItem(
                    manufacturer=Manufacturer(row["manufacturer_name"]),
                    category=row["faq_category"] or "",
                    question=row["question"],
                    answer=row["answer"],
                    source_url=row["source_url"] or "",
                )
                for row in rows
            ]
        finally:
            cursor.close()

    def create_faq(self, faqitem: FAQItem) -> None:
        """FAQ 항목을 DB에 저장한다.

        faq_category 가 없으면 자동으로 생성한다.

        Args:
            faqitem: 저장할 FAQItem 객체.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM manufacturer WHERE name = %s",
                (faqitem.manufacturer.value,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"제조사를 찾을 수 없습니다: {faqitem.manufacturer.value}")
            manufacturer_id = row[0]

            cursor.execute(
                "SELECT id FROM faq_category WHERE category = %s",
                (faqitem.category,),
            )
            row = cursor.fetchone()
            if row is None:
                cursor.execute(
                    "INSERT INTO faq_category (category) VALUES (%s)",
                    (faqitem.category,),
                )
                faq_category_id = cursor.lastrowid
            else:
                faq_category_id = row[0]

            cursor.execute(
                """
                INSERT INTO faq (manufacturer_id, faq_category_id, question, answer, source_url)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    manufacturer_id,
                    faq_category_id,
                    faqitem.question,
                    faqitem.answer,
                    faqitem.source_url,
                ),
            )
            conn.commit()
        finally:
            cursor.close()

    def find_subsidy(self, region: Region, vehicle: ElectricVehicle) -> Subsidy:
        """지역과 차종으로 보조금 정보를 조회한다."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT *
                FROM v_subsidy_detail
                WHERE region_name = %s
                  AND model_name = %s
                ORDER BY year DESC
                LIMIT 1
                """,
                (region.value, vehicle.model_name),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Subsidy(
                year=row["year"],
                region=region,
                electric_vehicle=vehicle,
                national_subsidy=row["national_subsidy"],
                local_subsidy=row["local_subsidy"],
                national_conversion_subsidy=row["national_conversion_subsidy"] or 0,
                local_conversion_subsidy=row["local_conversion_subsidy"] or 0,
            )
        finally:
            cursor.close()

    def create_subsidy(self, subsidy: Subsidy) -> None:
        """보조금 정보를 DB에 저장한다."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM electric_vehicle WHERE model_name = %s",
                (subsidy.electric_vehicle.model_name,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"전기차를 찾을 수 없습니다: {subsidy.electric_vehicle.model_name}")
            electric_vehicle_id = row[0]

            cursor.execute(
                "SELECT id FROM region WHERE name = %s",
                (subsidy.region.value,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"지역을 찾을 수 없습니다: {subsidy.region.value}")
            region_id = row[0]

            cursor.execute(
                """
                INSERT INTO subsidy (
                    electric_vehicle_id, region_id, year,
                    national_subsidy, local_subsidy,
                    national_conversion_subsidy, local_conversion_subsidy
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    electric_vehicle_id,
                    region_id,
                    subsidy.year,
                    subsidy.national_subsidy,
                    subsidy.local_subsidy,
                    subsidy.national_conversion_subsidy,
                    subsidy.local_conversion_subsidy,
                ),
            )
            conn.commit()
        finally:
            cursor.close()

    def find_all_vehicle(self) -> list[ElectricVehicle]:
        """전기차 전체 목록을 조회한다."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM v_electric_vehicle_detail")
            rows = cursor.fetchall()
            vehicles = []
            for row in rows:
                vehicle = ElectricVehicle(
                    manufacturer=Manufacturer(row["manufacturer_name"]),
                    model_name=row["model_name"],
                    trim_name=row["trim_name"],
                    price=row["price"],
                    driving_range=row["driving_range"],
                    efficiency=row["efficiency"],
                    slow_charging_type=ChargingType(row["slow_charging_type_name"]) if row["slow_charging_type_name"] else None,
                    fast_charging_type=ChargingType(row["fast_charging_type_name"]) if row["fast_charging_type_name"] else None,
                )
                vehicles.append(vehicle)
            return vehicles
        finally:
            cursor.close()

    def create_vehicle(self, vehicle: ElectricVehicle) -> None:
        """전기차 정보를 DB에 저장한다."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM manufacturer WHERE name = %s",
                (vehicle.manufacturer.value,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"제조사를 찾을 수 없습니다: {vehicle.manufacturer.value}")
            manufacturer_id = row[0]

            cursor.execute(
                "SELECT id FROM charging_type WHERE name = %s",
                (vehicle.slow_charging_type.value,),
            )
            row = cursor.fetchone()
            slow_charging_type_id = row[0] if row else None

            cursor.execute(
                "SELECT id FROM charging_type WHERE name = %s",
                (vehicle.fast_charging_type.value,),
            )
            row = cursor.fetchone()
            fast_charging_type_id = row[0] if row else None

            cursor.execute(
                """
                INSERT INTO electric_vehicle (
                    manufacturer_id, model_name, trim_name,
                    price, driving_range, efficiency,
                    slow_charging_type_id, fast_charging_type_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    manufacturer_id,
                    vehicle.model_name,
                    vehicle.trim_name,
                    vehicle.price,
                    vehicle.driving_range,
                    vehicle.efficiency,
                    slow_charging_type_id,
                    fast_charging_type_id,
                ),
            )
            conn.commit()
        finally:
            cursor.close()

    def find_ev_count_by_region(self, region: Region) -> RegionEVStats:
        """지역별 전기차 등록대수를 조회한다."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT region_name, year, ev_count
                FROM v_ev_registration_by_region
                WHERE region_name = %s
                ORDER BY year DESC
                LIMIT 1
                """,
                (region.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return RegionEVStats(
                electric_vehicle_count=row["ev_count"],
                population=0,
                region=region,
                year=row["year"],
                base_date=str(row["year"]),
            )
        finally:
            cursor.close()
    
    def create_ev_count_by_region(self, ev_stats: RegionEVStats) -> None:
        """지역별 전기차 등록대수를 DB에 저장한다."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM region WHERE name = %s",
                (ev_stats.region.value,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"지역을 찾을 수 없습니다: {ev_stats.region.value}")
            region_id = row[0]

            cursor.execute(
                """
                INSERT INTO ev_registration (region_id, year, ev_count)
                VALUES (%s, %s, %s)
                """,
                (region_id, ev_stats.year, ev_stats.electric_vehicle_count),
            )
            conn.commit()
        finally:
            cursor.close()

    def find_city(self, region: Region, city: str) -> str | None:
        """시도와 시/군/구명으로 도시를 조회한다."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT city_name FROM v_city_by_region WHERE region_name = %s AND city_name = %s",
                (region.value, city),
            )
            row = cursor.fetchone()
            return row["city_name"] if row else None
        finally:
            cursor.close()

    def find_population_by_region(self, region: Region) -> RegionEVStats:
        """지역별 인구수 통계를 조회한다."""
        pass

    def find_charging_station(self, region: Region, city: str) -> list[ChargingStation]:
        """지역과 도시로 충전소 목록을 조회한다."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM v_charging_station_map WHERE region_name = %s AND city_name = %s",
                (region.value, city),
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                cs = ChargingStation()
                cs.name = row["name"]
                cs.region = region
                cs.city = row["city_name"] or ""
                cs.latitude = row["latitude"]
                cs.longitude = row["longitude"]
                cs.available_time = f"{row['start_time']} - {row['close_time']}"
                cs.contact = row["contact"] or ""
                cs.charging_type = row["charging_type_name"] or ""
                result.append(cs)
            return result
        finally:
            cursor.close()

    def create_charging_station(self, charging_station) -> None:
        """충전소 정보를 DB에 저장한다."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM region WHERE name = %s",
                (charging_station.region.value,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"지역을 찾을 수 없습니다: {charging_station.region.value}")
            region_id = row[0]

            city_id = None
            if charging_station.city:
                cursor.execute(
                    "SELECT id FROM city WHERE name = %s AND region_id = %s",
                    (charging_station.city, region_id),
                )
                row = cursor.fetchone()
                if row:
                    city_id = row[0]

            charging_type_id = None
            if charging_station.charging_type:
                cursor.execute(
                    "SELECT id FROM charging_type WHERE name = %s",
                    (charging_station.charging_type,),
                )
                row = cursor.fetchone()
                if row:
                    charging_type_id = row[0]

            cursor.execute(
                """
                INSERT INTO charging_station (
                    name, region_id, city_id, address,
                    latitude, longitude, contact,
                    start_time, close_time, charging_type_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    charging_station.name,
                    region_id,
                    city_id,
                    getattr(charging_station, "address", None),
                    charging_station.latitude,
                    charging_station.longitude,
                    charging_station.contact,
                    charging_station.start_time,
                    charging_station.close_time,
                    charging_type_id,
                ),
            )
            conn.commit()
        finally:
            cursor.close()

    def find_repair_shop(self, region: Region, city: str) -> list[RepairShop]:
        """지역과 도시로 정비소 목록을 조회한다."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM v_repair_shop_map WHERE region_name = %s AND city_name = %s",
                (region.value, city),
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                rs = RepairShop()
                rs.name = row["name"]
                rs.region = region
                rs.city = row["city_name"] or ""
                rs.latitude = row["latitude"]
                rs.longitude = row["longitude"]
                rs.available_time = f"{row['start_time']} - {row['close_time']}"
                rs.contact = row["contact"] or ""
                rs.repair_shop_type = row["repair_shop_type_name"] or ""
                result.append(rs)
            return result
        finally:
            cursor.close()

    def create_repair_shop(self, repair_shop) -> None:
        """정비소 정보를 DB에 저장한다."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM region WHERE name = %s",
                (repair_shop.region.value,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"지역을 찾을 수 없습니다: {repair_shop.region.value}")
            region_id = row[0]

            city_id = None
            if repair_shop.city:
                cursor.execute(
                    "SELECT id FROM city WHERE name = %s AND region_id = %s",
                    (repair_shop.city, region_id),
                )
                row = cursor.fetchone()
                if row:
                    city_id = row[0]

            repair_shop_type_id = None
            if repair_shop.repair_shop_type:
                cursor.execute(
                    "SELECT id FROM repair_shop_type WHERE name = %s",
                    (repair_shop.repair_shop_type,),
                )
                row = cursor.fetchone()
                if row:
                    repair_shop_type_id = row[0]

            cursor.execute(
                """
                INSERT INTO repair_shop (
                    name, region_id, city_id, address,
                    latitude, longitude, contact,
                    start_time, close_time, repair_shop_type_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    repair_shop.name,
                    region_id,
                    city_id,
                    getattr(repair_shop, "address", None),
                    repair_shop.latitude,
                    repair_shop.longitude,
                    repair_shop.contact,
                    repair_shop.start_time,
                    repair_shop.close_time,
                    repair_shop_type_id,
                ),
            )
            conn.commit()
        finally:
            cursor.close()

    def find_adoption_rate_by_region(self, region: Region) -> RegionEVStats:
        """지역별 전기차 보급률 통계를 조회한다."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT region_name, adoption_rate
                FROM v_adoption_rate_by_region
                WHERE region_name = %s
                """,
                (region.value,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return RegionEVStats(
                electric_vehicle_count=0,
                population=row["adoption_rate"],
                region=region,
                year=0,
                base_date="",
            )
        finally:
            cursor.close()

