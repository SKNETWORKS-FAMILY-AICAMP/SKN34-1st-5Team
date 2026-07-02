"""dashboard_page.py

역할
- 전기차 모델과 지역을 선택하면 차량 기본 정보, 예상 유지비, 지역별 보조금,
  예상 구매 가격, 지역별 등록 현황, 인구 대비 보유율을 한 화면에서 보여주는
  대시보드 페이지.

주의
- DB(테이블)에 데이터가 아직 적재되지 않았거나 DB에 연결할 수 없는 경우,
  화면 레이아웃을 확인할 수 있도록 샘플 데이터로 대체해서 보여준다.
  샘플 데이터가 쓰인 항목에는 "샘플 데이터" 배지를 표시한다.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

from src.service import electric_vehicle_service, subsidy_service
from src.service.statistics_service import StatisticsService
from src.type.charging_type import ChargingType
from src.type.electric_vehicle import ElectricVehicle
from src.type.manufacturer import Manufacturer
from src.type.region import Region
from src.type.region_EV_stats import RegionEVStats
from src.type.subsidy import Subsidy

# 유지비(연료비) 비교 계산기의 기본값
DEFAULT_FUEL_PRICE_PER_LITER = 1_600  # 기름값(₩/리터당) 기본값
DEFAULT_FUEL_EFFICIENCY_KM_PER_L = 9.0  # 내연기관 연비(km/L) 기본값
DEFAULT_ELECTRICITY_PRICE_PER_KWH = 300  # 충전요금(₩/kWh당) 기본값
DEFAULT_ANNUAL_MILEAGE_KM = 10_000  # 연간 주행거리(km) 기본값
DEFAULT_DRIVING_YEARS = 1  # 운행 기간(년) 기본값

# DB에 데이터가 없을 때 화면 미리보기용으로 쓰는 샘플 차량 목록
SAMPLE_VEHICLES = [
    ElectricVehicle(
        manufacturer=Manufacturer.HYUNDAI,
        model_name="아이오닉 5",
        trim_name="롱레인지 2WD",
        price=5200,
        driving_range=458,
        efficiency=5.1,
        slow_charging_type=ChargingType.AC_SINGLE_PHASE_5_PIN,
        fast_charging_type=ChargingType.DC_COMBO_1,
    ),
    ElectricVehicle(
        manufacturer=Manufacturer.KIA,
        model_name="EV6",
        trim_name="어스 4WD",
        price=5700,
        driving_range=430,
        efficiency=4.5,
        slow_charging_type=ChargingType.AC_SINGLE_PHASE_5_PIN,
        fast_charging_type=ChargingType.DC_COMBO_1,
    ),
]


def _sample_subsidy(region: Region, vehicle: ElectricVehicle) -> Subsidy:
    return Subsidy(
        year=2025,
        region=region,
        electric_vehicle=vehicle,
        national_subsidy=650,
        local_subsidy=200,
        national_conversion_subsidy=0,
        local_conversion_subsidy=0,
    )


def _sample_registration_stats(region: Region) -> RegionEVStats:
    return RegionEVStats(
        electric_vehicle_count=45231,
        population=0,
        region=region,
        year=2025,
        base_date="2025",
    )


def _sample_adoption_stats(region: Region) -> RegionEVStats:
    return RegionEVStats(
        electric_vehicle_count=0,
        population=8.42,
        region=region,
        year=0,
        base_date="",
    )


def _sample_badge() -> None:
    st.caption(":orange[⚠️ DB에 데이터가 없어 샘플 데이터로 표시 중입니다.]")


st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .block-container p, .block-container li, .block-container label { font-size: 1.15rem; }
    [data-testid="stMetricValue"] { font-size: 2.1rem; }
    [data-testid="stMetricLabel"] { font-size: 1.1rem; }
    [data-testid="stCaptionContainer"] { font-size: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔋 전기차 구매 대시보드")
st.caption("모델과 지역을 선택하면 차량 정보와 지역별 혜택을 한눈에 확인할 수 있어요")
st.divider()


try:
    vehicles = electric_vehicle_service.get_all()
except Exception:
    vehicles = []

using_sample_vehicles = not vehicles
if using_sample_vehicles:
    vehicles = SAMPLE_VEHICLES
    st.info("DB에 등록된 전기차 데이터가 없어 샘플 데이터로 화면을 미리 보여줍니다.")

vehicle_options = {
    f"{vehicle.model_name} - {vehicle.trim_name or '기본'}": (vehicle.model_name, vehicle.trim_name)
    for vehicle in vehicles
}

col_dropdown1, col_dropdown2 = st.columns(2)
with col_dropdown1:
    selected_vehicle_label = st.selectbox("전기차 모델", list(vehicle_options.keys()))
    selected_model_name, selected_trim_name = vehicle_options[selected_vehicle_label]
with col_dropdown2:
    region_options = {region.value: region for region in Region}
    selected_region_name = st.selectbox("지역 선택", list(region_options.keys()))
    selected_region = region_options[selected_region_name]

if using_sample_vehicles:
    selected_vehicle = next(
        vehicle
        for vehicle in SAMPLE_VEHICLES
        if vehicle.model_name == selected_model_name and vehicle.trim_name == selected_trim_name
    )
else:
    try:
        selected_vehicle = electric_vehicle_service.get_by_vehicle(selected_model_name, selected_trim_name)
    except Exception:
        selected_vehicle = None

    if selected_vehicle is None:
        st.error(f"{selected_vehicle_label} 상세 정보를 불러오지 못했습니다.")
        st.stop()

st.divider()


left_col, right_col = st.columns(2)

with left_col:
    with st.container(border=True):
        st.subheader("선택된 전기차 기본 정보")
        if using_sample_vehicles:
            _sample_badge()

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"**제조사**: {selected_vehicle.manufacturer.value}")
            st.markdown(f"**모델명**: {selected_vehicle.model_name}")
            st.markdown(f"**트림**: {selected_vehicle.trim_name or '-'}")
            st.markdown(f"**가격**: {selected_vehicle.price:,}만원")
        with info_col2:
            st.markdown(f"**1회 충전 주행거리**: {selected_vehicle.driving_range:,.0f}km")
            st.markdown(f"**복합 전비**: {selected_vehicle.efficiency:.1f}km/kWh")
            st.markdown(
                "**완속 충전 타입**: "
                f"{selected_vehicle.slow_charging_type.value if selected_vehicle.slow_charging_type else '-'}"
            )
            st.markdown(
                "**급속 충전 타입**: "
                f"{selected_vehicle.fast_charging_type.value if selected_vehicle.fast_charging_type else '-'}"
            )

    with st.container(border=True):
        st.subheader("예상 유지비 비용")

        mileage_col, years_col = st.columns(2)
        with mileage_col:
            annual_mileage = st.number_input(
                "연간 주행거리 (km/1년)", min_value=0, value=DEFAULT_ANNUAL_MILEAGE_KM, step=500
            )
        with years_col:
            driving_years = st.number_input(
                "운행 기간 (년)", min_value=1, value=DEFAULT_DRIVING_YEARS, step=1
            )

        st.markdown("🛢️ **내연기관**")
        fuel_price_col, fuel_efficiency_col, ice_cost_col = st.columns(3)
        with fuel_price_col:
            fuel_price = st.number_input(
                "기름값 (₩/리터당)", min_value=0, value=DEFAULT_FUEL_PRICE_PER_LITER, step=50
            )
        with fuel_efficiency_col:
            fuel_efficiency = st.number_input(
                "연비 (km/L)", min_value=0.1, value=DEFAULT_FUEL_EFFICIENCY_KM_PER_L, step=0.1
            )
        ice_annual_cost = (annual_mileage / fuel_efficiency) * fuel_price
        with ice_cost_col:
            st.metric("연간 유류비", f"{ice_annual_cost:,.0f}원")

        st.markdown("⚡ **전기차**")
        electricity_price_col, ev_efficiency_col, ev_cost_col = st.columns(3)
        with electricity_price_col:
            electricity_price = st.number_input(
                "충전요금 (₩/kWh당)", min_value=0, value=DEFAULT_ELECTRICITY_PRICE_PER_KWH, step=10
            )
        with ev_efficiency_col:
            ev_efficiency = st.number_input(
                "전비 (km/kWh)",
                min_value=0.1,
                value=float(selected_vehicle.efficiency) if selected_vehicle.efficiency else 5.0,
                step=0.1,
            )
        ev_annual_cost = (annual_mileage / ev_efficiency) * electricity_price
        with ev_cost_col:
            st.metric("연간 전기료", f"{ev_annual_cost:,.0f}원")

        total_savings = (ice_annual_cost - ev_annual_cost) * driving_years

        st.divider()
        if total_savings >= 0:
            st.markdown(
                f"### 전기차 구매 시 {driving_years}년간 :green[{total_savings:,.0f}원] 절감할 수 있어요!"
            )
        else:
            st.markdown(
                f"### 전기차 구매 시 {driving_years}년간 :red[{abs(total_savings):,.0f}원] 더 들 수 있어요."
            )
        st.caption("엔진오일 교체비용, 하이패스/공영주차장 할인 등 부가적인 절감 효과도 있어요.")

with right_col:
    with st.container(border=True):
        st.subheader("지역별 해당 모델 보조금")
        try:
            subsidy = subsidy_service.get_subsidy(selected_region, selected_vehicle)
        except Exception:
            subsidy = None

        is_sample_subsidy = subsidy is None
        if is_sample_subsidy:
            subsidy = _sample_subsidy(selected_region, selected_vehicle)
            _sample_badge()

        st.markdown(f"**국고 보조금**: {subsidy.national_subsidy:,}만원")
        st.markdown(f"**지방 보조금**: {subsidy.local_subsidy:,}만원")
        st.markdown(f"**보조금 합계**: {subsidy.get_total_support_amount():,}만원")

    with st.container(border=True):
        st.subheader("예상 구매 가격")
        if is_sample_subsidy:
            _sample_badge()
        expected_price = max(selected_vehicle.price - subsidy.get_total_support_amount(), 0)
        st.markdown(f"보조금 적용 예상 가격: **{expected_price:,}만원**")
        st.caption(f"차량 가격 {selected_vehicle.price:,}만원에서 보조금 합계를 뺀 금액입니다.")

    with st.container(border=True):
        st.subheader("지역별 전기차 등록 현황")
        try:
            registration_stats = StatisticsService().get_ev_registration_by_region(
                year=None, region=selected_region
            )
        except Exception:
            registration_stats = None

        if registration_stats is None:
            registration_stats = _sample_registration_stats(selected_region)
            _sample_badge()

        st.markdown(f"{registration_stats.year}년 등록대수: **{registration_stats.electric_vehicle_count:,}대**")

    with st.container(border=True):
        st.subheader("지역별 인구 대비 전기차 보유율")
        try:
            adoption_stats = StatisticsService().get_ev_adoption_rate_by_population(
                year=None, region=selected_region
            )
        except Exception:
            adoption_stats = None

        if adoption_stats is None:
            adoption_stats = _sample_adoption_stats(selected_region)
            _sample_badge()

        st.markdown(f"인구 대비 전기차 보유율: **{adoption_stats.population:,.2f}%**")
