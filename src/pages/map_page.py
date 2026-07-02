import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


import streamlit as st
import streamlit.components.v1 as 
from src.repository.repository import Repository
from src.service.location_service import get_charging_station_by_region as gcs, get_repair_shop_by_region as grs, get_city as gc
from src.type.repair_shop import RepairShop
from src.type.location import Location
from src.type.page import Page 
from src.type.region import Region

# UI
st.set_page_config(layout="wide")
st.title("충전소 위치 검색")
st.caption("가까운 충전소 위치를 찾아보세요")
st.divider()

private_key = "db52e0844a15f0ae284d2f7853dc6ef3"

# Map Sector
db = Repository()
charge_station = "친환경 충전소"
adress = "서울 강남구"

col1, col2 = st.columns([1.5, 6], gap="medium", vertical_alignment="top")

with col1:
    region_box = st.selectbox(
        "지역을 선택하세요",
        region_select = [Region],
        key="sigungu_select"
    )

    
 
    city_box = st.selectbox(
        "시/군/구 를 선택하세요",
        db.find_city(),
        key="city_select"
    )

    with st.container(border=True):
        st.markdown(f"###### ⚡ {charge_station}   <span style='font-size:12px; background-color:green; color:white; padding:3px 8px; border-radius:10px;'>충전소</span>", unsafe_allow_html=True)
        st.caption(f"📍 {adress}")
    

with col2:
        with st.container():
            map_html ="""
            <div style="display: flex; width: 200%;"> 
                <div id="map" style="width: 85%; aspect-ratio: 1 / 1;  background-color: skyblue; padding: 20px; box-sizing: border-box;">
                    <div style="position: absolute; top: 1%; left: 1%; width: 100%; height: 100%; z-index: 999; pointer-events: none;">
                    </div>
                </div>
                <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey=db52e0844a15f0ae284d2f7853dc6ef3"></script>
                <script type="text/javascript">
                    var container = document.getElementById('map');
                    var options = {
                        center: new kakao.maps.LatLng(37.5665, 126.9780), // 서울시청
                        level: 3
                    };
                    // 스크립트가 로드되면 바로 지도를 생성합니다.
                    var map = new kakao.maps.Map(container, options);
                </script>
            </div>
                
            """

        components.html(map_html, height=800)