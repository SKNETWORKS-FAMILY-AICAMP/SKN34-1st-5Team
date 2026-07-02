from types import SimpleNamespace

import pytest

from src.service import location_service
from src.type.region import Region


class FakeRepository:
    charging_stations = []
    repair_shops = []
    cities = []
    created_charging_stations = []
    created_repair_shops = []

    def find_charging_station(self, region, city):
        self.last_charging_station_args = (region, city)
        return self.charging_stations

    def find_repair_shop(self, region, city):
        self.last_repair_shop_args = (region, city)
        return self.repair_shops

    def find_city(self, region):
        self.last_city_args = (region,)
        return self.cities

    def create_charging_station(self, location):
        self.created_charging_stations.append(location)

    def create_repair_shop(self, repair_shop):
        self.created_repair_shops.append(repair_shop)


@pytest.fixture
def fake_repository(monkeypatch):
    fake = FakeRepository()
    fake.created_charging_stations = []
    fake.created_repair_shops = []
    monkeypatch.setattr(location_service, "Repository", lambda: fake)
    return fake


def test_get_charging_station_by_region_returns_requested_page(fake_repository):
    fake_repository.charging_stations = [
        SimpleNamespace(name="station-1"),
        SimpleNamespace(name="station-2"),
        SimpleNamespace(name="station-3"),
        SimpleNamespace(name="station-4"),
        SimpleNamespace(name="station-5"),
    ]

    page = location_service.get_charging_station_by_region(
        region=Region.SEOUL,
        city="강남구",
        page=2,
        size=2,
    )

    assert [item.name for item in page.item] == ["station-3", "station-4"]
    assert page.total_page == 3
    assert page.current_page == 2
    assert fake_repository.last_charging_station_args == (Region.SEOUL, "강남구")


def test_get_repair_shop_by_region_returns_requested_page(fake_repository):
    fake_repository.repair_shops = [
        SimpleNamespace(name="shop-1"),
        SimpleNamespace(name="shop-2"),
        SimpleNamespace(name="shop-3"),
    ]

    page = location_service.get_repair_shop_by_region(
        region=Region.BUSAN,
        city="해운대구",
        page=1,
        size=2,
    )

    assert [item.name for item in page.item] == ["shop-1", "shop-2"]
    assert page.total_page == 2
    assert page.current_page == 1
    assert fake_repository.last_repair_shop_args == (Region.BUSAN, "해운대구")


def test_get_location_services_return_empty_page_for_empty_results(fake_repository):
    fake_repository.charging_stations = []
    fake_repository.repair_shops = []

    charging_page = location_service.get_charging_station_by_region(
        region=Region.SEOUL,
        city="강남구",
        page=1,
        size=10,
    )
    repair_page = location_service.get_repair_shop_by_region(
        region=Region.SEOUL,
        city="강남구",
        page=1,
        size=10,
    )

    assert charging_page.item == []
    assert charging_page.total_page == 0
    assert repair_page.item == []
    assert repair_page.total_page == 0


def test_get_city_delegates_to_repository(fake_repository):
    fake_repository.cities = ["강남구", "서초구"]

    cities = location_service.get_city(Region.SEOUL)

    assert cities == ["강남구", "서초구"]
    assert fake_repository.last_city_args == (Region.SEOUL,)


def test_set_charging_station_by_region_raises_for_missing_file(fake_repository):
    with pytest.raises(FileNotFoundError):
        location_service.set_charging_station_by_region("missing.csv")


def test_set_repair_shop_by_region_raises_for_missing_file(fake_repository):
    with pytest.raises(FileNotFoundError):
        location_service.set_repair_shop_by_region("missing.csv")


def test_set_charging_station_by_region_loads_csv_row(tmp_path, fake_repository):
    csv_path = tmp_path / "charging.csv"
    csv_path.write_text(
        "name,region,address,latitude,longitude,available_time\n"
        "테스트충전소,서울특별시,강남구 테헤란로 1,37.1,127.1,24시간\n",
        encoding="utf-8",
    )

    location_service.set_charging_station_by_region(str(csv_path))

    assert len(fake_repository.created_charging_stations) == 1
    location = fake_repository.created_charging_stations[0]
    assert location.name == "테스트충전소"
    assert location.region == Region.SEOUL
    assert location.city == "강남구"
    assert location.address == "테헤란로 1"
    assert location.contact == ""


def test_set_repair_shop_by_region_loads_csv_row_with_contac_header(tmp_path, fake_repository):
    csv_path = tmp_path / "repair.csv"
    csv_path.write_text(
        "name,repair_shop_type,repair_scope,contac,region,address,latitude,longitude,available_time\n"
        "테스트정비소,현대,전 작업,02-1234-5678,서울특별시,강남구 테헤란로 2,37.2,127.2,09:00 ~ 18:00\n",
        encoding="utf-8",
    )

    location_service.set_repair_shop_by_region(str(csv_path))

    assert len(fake_repository.created_repair_shops) == 1
    repair_shop = fake_repository.created_repair_shops[0]
    assert repair_shop.name == "테스트정비소"
    assert repair_shop.region == Region.SEOUL
    assert repair_shop.city == "강남구"
    assert repair_shop.address == "테헤란로 2"
    assert repair_shop.contact == "02-1234-5678"
