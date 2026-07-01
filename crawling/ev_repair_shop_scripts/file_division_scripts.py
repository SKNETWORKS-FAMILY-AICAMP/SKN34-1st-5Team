import pandas as pd

INPUT_FILE = "kakaomap_final_processed.csv"   
OUTPUT_FILE = "kakaomap_split_complete.csv"   

TARGET_COL = "도로명주소"               # 기준이 되는 주소 열 이름
# =====================================================================

print(f"📊 1. CSV 파일('{INPUT_FILE}') 로드 중...")
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

if TARGET_COL in df.columns:
    print(f"⚡ 2. '{TARGET_COL}' 자리에 'region'과 'address' 열 삽입 중...")
    
    # 도로명 주소가 있는 열의 '인덱스' 추적
    target_idx = df.columns.get_loc(TARGET_COL)
    
    # 첫 번째 공백 기준 주소 쪼개기
    split_addr = df[TARGET_COL].astype(str).str.split(' ', n=1, expand=True)
    
    # df.insert(위치번호, '열이름', 넣을데이터)
    df.insert(target_idx, 'region', split_addr[0].fillna(''))
    df.insert(target_idx + 1, 'address', split_addr[1].fillna(''))
    
    # '도로명주소' 열 삭제
    df = df.drop(columns=[TARGET_COL])
    
    print("교체 완료")
    
    # 결과 미리보기 출력
    print("\n미리보기")
    print(df.head(2)) # 전체 열 구조와 데이터 상위 2줄 출력
    
else:
    print(f" '{TARGET_COL}' 컬럼을 찾을 수 없습니다.")

# 5. 최종 결과 저장
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"\n'{OUTPUT_FILE}' 저장")