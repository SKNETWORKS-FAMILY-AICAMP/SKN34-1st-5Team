import pandas as pd

INPUT_FILE = "final_charge_station.csv"          
OUTPUT_FILE = "ev_charging_station_locations.csv"       

REGION_COL = "지역"                        
ADDRESS_COL = "주소"                      
# =====================================================================

print(f"CSV 파일 로드 ({INPUT_FILE})")
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# 열 이름 유령 공백 방어
df.columns = df.columns.str.strip()

# 지역 열 데이터 자체의 앞뒤 공백을 미리 싹 제거합니다.
df[REGION_COL] = df[REGION_COL].astype(str).str.strip()

# 변환 전 원본 데이터를 눈으로 확인하기 위해 임시 백업
df['address_original'] = df[ADDRESS_COL].copy()

def remove_duplicate_region(row):
    region_val = str(row[REGION_COL]).strip()
    address_val = str(row[ADDRESS_COL]).strip()
    
    if address_val.startswith(region_val):
        return address_val[len(region_val):].lstrip()
    return address_val

print("중복 제거")
df[ADDRESS_COL] = df.apply(remove_duplicate_region, axis=1)

# 위도(latitude)나 경도(longitude) 중 하나라도 결측치(NaN)이거나 '정보없음'인 행 제거
if 'latitude' in df.columns and 'longitude' in df.columns:
    print("위도/경도 '정보없음' 및 결측치 행 제거")
    df = df.dropna(subset=['latitude', 'longitude'])
    df = df[(df['latitude'].astype(str).str.strip() != '정보없음') & 
            (df['longitude'].astype(str).str.strip() != '정보없음')]

print("진행 상황")

preview_df = df[[REGION_COL, 'address_original', ADDRESS_COL]].head(10)
for idx, row in preview_df.iterrows():
    print(f"[{idx+1}번 행] {row[REGION_COL]} | {row['address_original']} ➡️ {row[ADDRESS_COL]}")

# 역할이 끝난 원본 백업 열 제거
df = df.drop(columns=['address_original'])

print(f"저장중...")
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"저장완료: '{OUTPUT_FILE}'")