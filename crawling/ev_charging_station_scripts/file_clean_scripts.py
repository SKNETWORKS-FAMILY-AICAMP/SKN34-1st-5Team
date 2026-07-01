import pandas as pd


INPUT_FILE = "charge_station.csv"          
OUTPUT_FILE = "charge_station_01.csv"    
# =====================================================================

print(f" CSV 파일('{INPUT_FILE}') 로드")
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
initial_rows = len(df)

# 컬럼명 유령 공백 제거
df.columns = df.columns.str.strip()

# ---------------------------------------------------------------------
#  '운영중지' 또는 '알수없음'을 포함하는 행 삭제
# ---------------------------------------------------------------------
if '충전기상태' in df.columns:
    status_series = df['충전기상태'].astype(str)
    
    # '운영중지' 또는 '알수없음' 포함 여부 체크
    condition_to_drop = status_series.str.contains('운영중지', na=False) | status_series.str.contains('알수없음', na=False)
    
    df = df[~condition_to_drop]
    deleted_rows = initial_rows - len(df)
    print(f"✂️ 2. '운영중지' 및 '알수없음' 포함 행 제거 완료 (총 {deleted_rows:,}개 행 삭제됨)")
else:
    print("'충전기상태' 컬럼을 찾을 수 없습니다.")

# ---------------------------------------------------------------------
#  대분류 '지번 주소' 칸 자체를 날리기
# ---------------------------------------------------------------------
if '지번 주소' in df.columns:
    # 💡 columns=['지번 주소']를 drop 하면 대분류 헤더와 그 내용이 통째로 삭제됩니다.
    df = df.drop(columns=['지번 주소','시군구', '운영기관', '충전기ID', '충전기상태', '시설구분(대)', '시설구분(소)', '상세위치', '이용자 제한', '충전용량', '편의제공', '비고','충전기타입'])
    print("🗑️ 3. 대분류 '지번 주소' 열(Column) 자체를 흔적 없이 완전 삭제 완료!")
else:
    print(" '지번 주소' 컬럼을 찾을 수 없습니다")


# 최종 결과 저장
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"\n최종 남은 데이터 건수: {len(df):,}건 (기존: {initial_rows:,}건)")
print(f"'{OUTPUT_FILE}' 저장")