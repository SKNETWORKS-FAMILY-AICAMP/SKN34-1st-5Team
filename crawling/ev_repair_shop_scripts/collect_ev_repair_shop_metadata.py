import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


KAKAO_REST_KEY = "eb4b594c3d2e74d97349749ab5169e6c"
INPUT_FILE = "ev_repair_shops.csv"  
OUTPUT_FILE = "ev_repair_shops_location.csv" 
IS_TEST = False # False는 전체작업, True는 테스트 작업
# =====================================================================

# 1. 카카오 API 세팅
SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
api_headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}

# 2. 셀레니움 브라우저 설정
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

df_source = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
df = df_source.head(5).copy() if IS_TEST else df_source.copy()

scraped_addresses = []
scraped_lats = []    
scraped_lngs = []    
scraped_hours = []   

print("\n수집 시작...")

try:
    for idx, row in df.iterrows():
        keyword = str(row['업체명']).strip()
        
        addr = "수집실패"
        lat = "정보없음"
        lng = "정보없음"
        hour = "운영시간 정보 없음"
        place_url = ""
        
        # [Step 1] 카카오 API 주소/위경도 및 place_url 수집
        params = {"query": keyword, "size": 1}
        try:
            response = requests.get(SEARCH_URL, params=params, headers=api_headers, timeout=5)
            if response.status_code == 200:
                documents = response.json().get('documents', [])
                if documents:
                    first_place = documents[0]
                    addr = first_place.get('road_address_name', first_place.get('address_name', '주소정보없음')).strip()
                    lng = first_place.get('x', '정보없음') 
                    lat = first_place.get('y', '정보없음') 
                    place_url = first_place.get('place_url', '')
        except Exception as e:
            pass

        # [Step 2] 셀레니움 인터랙션 
        if place_url and "http" in place_url:
            try:
                driver.get(place_url)
                wait = WebDriverWait(driver, 5)
                
                # 펼치기 버튼 대기 후 클릭 
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.unit_default button")))
                toggle_btn = driver.find_element(By.CSS_SELECTOR, "div.unit_default button")
                
                aria_expanded = toggle_btn.get_attribute("aria-expanded")
                if aria_expanded != "true":
                    driver.execute_script("arguments[0].click();", toggle_btn)
                    time.sleep(0.8)
                
                
                target_css = "div.detail_info.info_operation div.detail_fold span.txt_detail"
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_css)))
                targets = driver.find_elements(By.CSS_SELECTOR, target_css)
                
                if targets:
                    
                    raw_text = " / ".join([t.text.strip() for t in targets if t.text.strip()]).replace("\n", " ")
                    
                    # 결합된 문장에 슬래시(/)가 있다면 앞부분만 제거
                    if "/" in raw_text:
                        hour = raw_text.split("/")[0].strip()
                    else:
                        hour = raw_text.strip()
                        
            except Exception as e:
                pass
                
        print(f"   [{idx+1}/{len(df)}] {keyword} ➡️ 주소: {addr} | 위도: {lat} | 경도: {lng} | 운영시간: {hour}")
        
        scraped_addresses.append(addr)
        scraped_lats.append(lat)
        scraped_lngs.append(lng)
        scraped_hours.append(hour)

    # 4대 핵심 데이터 프레임 매핑 및 저장
    df['도로명주소'] = scraped_addresses
    df['위도'] = scraped_lats
    df['경도'] = scraped_lngs
    df['운영시간'] = scraped_hours

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n 저장완료: '{OUTPUT_FILE}'")

finally:
    driver.quit()