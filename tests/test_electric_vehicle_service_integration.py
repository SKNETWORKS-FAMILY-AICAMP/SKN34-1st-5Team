import csv
from pathlib import Path

from src.repository.repository import Repository
from src.service.electric_vehicle_service import get_all, get_by_vehicle, get_manufacturer, set_vehicle
from src.type.charging_type import ChargingType
from src.type.electric_vehicle import ElectricVehicle
from src.type.manufacturer import Manufacturer


CHARGING_TYPE_ALIASES = {
    "DC콤보(7pin)": ChargingType.DC_COMBO_1,
    "AC 단상(5pin)": ChargingType.AC_SINGLE_PHASE_5_PIN,
    "차데모": ChargingType.CHADEMO,
    "AC 3상(7pin)": ChargingType.AC_THREE_PHASE_7_PIN,
}


def clean_ev_tables():
    conn = Repository().get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM electric_vehicle")
    cursor.execute("DELETE FROM charging_type")
    conn.commit()
    cursor.close()


def vehicle_from_csv_row(row):
    return ElectricVehicle(
        manufacturer=Manufacturer(row["제조사"]),
        model_name=row["모델명"],
        trim_name=row["세부트림"],
        price=int(row["가격"]),
        driving_range=int(float(row["1회충전주행거리"])),
        efficiency=float(row["복합전비"]),
        fast_charging_type=CHARGING_TYPE_ALIASES[row["급속"]],
        slow_charging_type=CHARGING_TYPE_ALIASES[row["완속"]],
    )


def load_sample_rows(limit=5):
    path = Path("db/data/hyundai_kia_ev_vehicle_metadata.csv")
    with path.open(encoding="utf-8-sig") as csv_file:
        rows = []
        for index, row in enumerate(csv.DictReader(csv_file)):
            if index >= limit:
                break
            rows.append(row)
        return rows


def test_electric_vehicle_csv_rows_load_into_database():
    clean_ev_tables()

    rows = load_sample_rows(limit=5)
    for row in rows:
        set_vehicle(vehicle_from_csv_row(row))

    vehicles = get_all()
    vehicle_by_trim = {vehicle.trim_name: vehicle for vehicle in vehicles}
    air_2wd = vehicle_by_trim["에어 2WD (A/T)"]

    assert len(vehicles) == 5
    assert air_2wd.manufacturer == Manufacturer.KIA
    assert air_2wd.model_name == "EV5"
    assert air_2wd.price == 4575
    assert air_2wd.fast_charging_type == ChargingType.DC_COMBO_1
    assert air_2wd.slow_charging_type == ChargingType.AC_SINGLE_PHASE_5_PIN


def test_get_by_vehicle_returns_loaded_vehicle():
    clean_ev_tables()

    row = load_sample_rows(limit=1)[0]
    set_vehicle(vehicle_from_csv_row(row))

    vehicle = get_by_vehicle("EV5", "에어 2WD (A/T)")

    assert vehicle is not None
    assert vehicle.manufacturer == Manufacturer.KIA
    assert vehicle.driving_range == 460
    assert vehicle.efficiency == 5.0


def test_get_manufacturer_returns_db_manufacturers_after_load():
    clean_ev_tables()

    row = load_sample_rows(limit=1)[0]
    set_vehicle(vehicle_from_csv_row(row))

    manufacturers = get_manufacturer()

    assert Manufacturer.KIA in manufacturers
