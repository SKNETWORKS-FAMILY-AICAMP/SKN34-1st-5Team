import requests
import pandas as pd


KAKAO_REST_KEY = "API KEY"
INPUT_FILE = "clean_no_duplicates.csv"           
OUTPUT_FILE = "charge_station.csv"  

ADDRESS_COL = "주소"                   # 검색 기준 열
IS_TEST = False                                # True면 5건만 테스트, False면 전체 가동
# =====================================================================

# 카카오 API 설정 (주소 검색 전용)
SEARCH_URL = "https://dapi.kakao.com/v2/local/search/address.json"
api_headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}

print(f"CSV 파일 로드({INPUT_FILE})")
df_source = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# 컬럼명 유령 공백 제거
df_source.columns = df_source.columns.str.strip()

# 테스트 모드 분기
df = df_source.head(5).copy() if IS_TEST else df_source.copy()

# 결과 값을 담을 빈 리스트
scraped_lats = []
scraped_lngs = []

print(f"카카오 API로 위도/경도 좌표 추출(테스트모드: {IS_TEST})")

if ADDRESS_COL in df.columns:
    for idx, row in df.iterrows():
        # 주소 열에서 값을 가져오기
        full_address = str(row[ADDRESS_COL]).strip()
        
        lat = "정보없음"
        lng = "정보없음"
        
        if full_address and full_address != "nan":
            try:
                params = {"query": full_address, "size": 1}
                response = requests.get(SEARCH_URL, params=params, headers=api_headers, timeout=5)
                
                if response.status_code == 200:
                    documents = response.json().get('documents', [])
                    if documents:
                        first_match = documents[0]
                        lng = first_match.get('x', '정보없음') # 경도(Longitude)
                        lat = first_match.get('y', '정보없음') # 위도(Latitude)
            except Exception as e:
                print(f" 에러 발생 (행 {idx+1}): {e}")
                
        scraped_lats.append(lat)
        scraped_lngs.append(lng)
        
        if (idx + 1) % 10 == 0 or IS_TEST:
            print(f"    진행중 [{idx+1}/{len(df)}] -> 주소: {full_address[:20]}... | 위도: {lat} | 경도: {lng}")

    # 3. 주소 열 바로 뒤에 새 열 삽입
    addr_idx = df.columns.get_loc(ADDRESS_COL)
    df.insert(addr_idx + 1, 'latitude', scraped_lats)
    df.insert(addr_idx + 2, 'longitude', scraped_lngs)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n파일 저장 '{OUTPUT_FILE}'")

else:
    print(f"파일에서 '{ADDRESS_COL}' 열을 찾을 수 없습니다.")