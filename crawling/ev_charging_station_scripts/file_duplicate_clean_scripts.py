import pandas as pd

INPUT_FILE = "charge_station_01.csv"          
OUTPUT_FILE = "charge_station_02.csv"       

ADDRESS_COL = "주소"                   # 중복 검사의 기준이 될 주소 열 이름
# =====================================================================

print(f"CSV 파일 로드 ({INPUT_FILE})")
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# 열 이름 양끝의 유령 공백 제거
df.columns = df.columns.str.strip()

if ADDRESS_COL in df.columns:
    initial_count = len(df)
    print(f"🔍 현재 전체 데이터 개수: {initial_count:,}건")
    print(f"⚡ '{ADDRESS_COL}' 열을 기준으로 중복값 제거 처리 중...")
    
    # 💡 drop_duplicates 옵션 설명:
    # subset=[ADDRESS_COL]: 지정한 주소 열만 보고 중복을 판단
    # keep='first': 완전히 똑같은 주소가 여러 개 있으면, 맨 위에 있는 첫 번째 행만 살리고 나머지는 제거
    df_cleaned = df.drop_duplicates(subset=[ADDRESS_COL], keep='first')
    
    final_count = len(df_cleaned)
    removed_count = initial_count - final_count
    
    print(f"중복 제거")
    print(f" - 원래 데이터 개수: {initial_count:,}건")
    print(f" - 제거된 중복 데이터: {removed_count:,}건")
    print(f" - 최종 남은 데이터 개수: {final_count:,}건")
    
    df_cleaned.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"'{OUTPUT_FILE}' 저장")

else:
    print(f" 에러: 파일에서 '{ADDRESS_COL}' 열을 찾을 수 없습니다.")
    print(list(df.columns))