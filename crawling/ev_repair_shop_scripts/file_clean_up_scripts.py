import pandas as pd


INPUT_FILE = "kakaomap_clean_result.csv"     
OUTPUT_FILE = "kakaomap_final_processed.csv" 
# =====================================================================

print(f"CSV 파일('{INPUT_FILE}') 로드 중...")
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
initial_rows = len(df)

# 컬럼명 유령 공백 제거
df.columns = df.columns.str.strip()

# '수집실패'를 포함하는 행 삭제

if '도로명주소' in df.columns:
    # 안전하게 문자열로 변환 후 검사
    addr_series = df['도로명주소'].astype(str)
    
    # '수집실패'라는 글자가 들어간 행을 제외(~)하고 살립니다.
    df = df[~addr_series.str.contains('수집실패', na=False)]
    deleted_rows = initial_rows - len(df)
    print(f"'수집실패' 포함 행 제거 완료 (총 {deleted_rows:,}개 행 삭제)")
else:
    print("'도로명주소' 컬럼을 찾을 수 없습니다. 파일의 열 이름을 확인해주세요.")


# '운영시간 정보 없음'을 'N'으로 변경

if '운영시간' in df.columns:
    # 여기서는 '운영시간 정보 없음' 글자 전체를 깔끔하게 'N'으로 바꿉니다.
    df['운영시간'] = df['운영시간'].astype(str).str.replace('운영시간 정보 없음', 'N', regex=False)
    print("'N'으로 치환 완료!")
else:
    print("'운영시간' 컬럼을 찾을 수 없습니다. 파일의 열 이름을 확인해주세요.")


df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"\n 남은 데이터 건수: {len(df):,}건 (기존: {initial_rows:,}건)")
print(f"'{OUTPUT_FILE}'로 새로 저장")