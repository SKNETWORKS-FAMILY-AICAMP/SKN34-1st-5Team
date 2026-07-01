"""DB 접근을 담당하는 Repository 모듈"""

import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector.connection import MySQLConnection

from src.type.electric_vehicle import ElectricVehicle
from src.type.faq_item import FAQItem
from src.type.manufacturer import Manufacturer
from src.type.region import Region
from src.type.region_EV_stats import RegionEVStats
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
        pass

    def create_subsidy(self, subsidy: Subsidy) -> None:
        """보조금 정보를 DB에 저장한다."""
        pass

    def find_all_vehicle(self) -> list[ElectricVehicle]:
        """전기차 전체 목록을 조회한다."""
        pass

    def create_vehicle(self, vehicle: ElectricVehicle) -> None:
        """전기차 정보를 DB에 저장한다."""
        pass

    def find_ev_count_by_region(self, region: Region) -> RegionEVStats:
        """지역별 전기차 등록대수를 조회한다."""
        pass

    def find_population_by_region(self, region: Region) -> RegionEVStats:
        """지역별 인구 통계를 조회한다."""
        pass

