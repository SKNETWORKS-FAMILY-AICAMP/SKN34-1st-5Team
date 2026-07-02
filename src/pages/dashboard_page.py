"""dashboard_page.py

역할
- 전기차 모델과 지역을 선택하면 차량 기본 정보, 예상 유지비, 지역별 보조금,
  예상 구매 가격, 지역별 등록 현황, 인구 대비 보유율을 한 화면에서 보여주는
  대시보드 페이지.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

from src.service import electric_vehicle_service, subsidy_service
from src.service.statistics_service import StatisticsService
from src.type.region import Region

# 유지비 추정에 사용하는 가정값 (실측 유지비 데이터가 없어 전비 기반으로 추정)
ANNUAL_MILEAGE_KM = 12_000  # 연간 평균 주행거리(km) 가정
ELECTRICITY_PRICE_PER_KWH = 173  # 완속충전 기준 전기요금(원/kWh) 가정


st.set_page_config(layout="wide")
st.title("🔋 전기차 구매 대시보드")
st.caption("모델과 지역을 선택하면 차량 정보와 지역별 혜택을 한눈에 확인할 수 있어요")
st.divider()


vehicles = electric_vehicle_service.get_all()

if not vehicles:
    st.warning("등록된 전기차 정보가 없습니다.")
    st.stop()

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

selected_vehicle = electric_vehicle_service.get_by_vehicle(selected_model_name, selected_trim_name)

if selected_vehicle is None:
    st.error(f"{selected_vehicle_label} 상세 정보를 불러오지 못했습니다.")
    st.stop()

st.divider()


left_col, right_col = st.columns(2)

with left_col:
    with st.container(border=True):
        st.subheader("선택된 전기차 기본 정보")
        st.markdown(f"**제조사**: {selected_vehicle.manufacturer.value}")
        st.markdown(f"**모델명**: {selected_vehicle.model_name}")
        st.markdown(f"**트림**: {selected_vehicle.trim_name or '-'}")
        st.markdown(f"**가격**: {selected_vehicle.price:,}만원")
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
        if selected_vehicle.efficiency:
            annual_kwh = ANNUAL_MILEAGE_KM / selected_vehicle.efficiency
            annual_cost = annual_kwh * ELECTRICITY_PRICE_PER_KWH
            st.metric("연간 예상 전기 충전 비용", f"{annual_cost:,.0f}원")
            st.caption(
                f"가정: 연간 주행거리 {ANNUAL_MILEAGE_KM:,}km, "
                f"완속충전 전기요금 {ELECTRICITY_PRICE_PER_KWH}원/kWh 기준 추정치"
            )
        else:
            st.info("전비 정보가 없어 유지비를 추정할 수 없습니다.")

with right_col:
    with st.container(border=True):
        st.subheader("지역별 해당 모델 보조금")
        try:
            subsidy = subsidy_service.get_subsidy(selected_region, selected_vehicle)
        except Exception:
            subsidy = None

        if subsidy is None:
            st.info(f"{selected_region_name} 지역의 {selected_vehicle.model_name} 보조금 정보가 없습니다.")
        else:
            st.markdown(f"**국고 보조금**: {subsidy.national_subsidy:,}만원")
            st.markdown(f"**지방 보조금**: {subsidy.local_subsidy:,}만원")
            st.markdown(f"**보조금 합계**: {subsidy.get_total_support_amount():,}만원")

    with st.container(border=True):
        st.subheader("예상 구매 가격")
        if subsidy is not None:
            expected_price = max(selected_vehicle.price - subsidy.get_total_support_amount(), 0)
            st.metric("보조금 적용 예상 가격", f"{expected_price:,}만원")
            st.caption(f"차량 가격 {selected_vehicle.price:,}만원에서 보조금 합계를 뺀 금액입니다.")
        else:
            st.metric("차량 가격", f"{selected_vehicle.price:,}만원")
            st.caption("지역 보조금 정보가 없어 차량 정가를 표시합니다.")

    with st.container(border=True):
        st.subheader("지역별 전기차 등록 현황")
        try:
            registration_stats = StatisticsService().get_ev_registration_by_region(
                year=None, region=selected_region
            )
        except Exception:
            registration_stats = None

        if registration_stats is None:
            st.info(f"{selected_region_name} 지역의 등록 현황 정보가 없습니다.")
        else:
            st.metric(
                f"{registration_stats.year}년 등록대수",
                f"{registration_stats.electric_vehicle_count:,}대",
            )

    with st.container(border=True):
        st.subheader("지역별 인구 대비 전기차 보유율")
        try:
            adoption_stats = StatisticsService().get_ev_adoption_rate_by_population(
                year=None, region=selected_region
            )
        except Exception:
            adoption_stats = None

        if adoption_stats is None:
            st.info(f"{selected_region_name} 지역의 보유율 정보가 없습니다.")
        else:
            st.metric("인구 천 명당 전기차 등록대수", f"{adoption_stats.population:,.2f}대")
