import pandas as pd

# =====================================================================
# ⚙️ [설정 영역] 파일명을 올바르게 입력해주세요.
# =====================================================================
INPUT_FILE = "kakaomap_split_complete.csv"   # 직전 단계에서 주소가 분할된 파일명
OUTPUT_FILE = "kakaomap_final_perfect.csv"   # 모든 정제가 끝난 최종 마스터 파일명
# =====================================================================

print(f"📊 1. 주소 분할 파일('{INPUT_FILE}') 로드 중...")
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# 혹시 모를 양끝 공백 제거
if 'region' in df.columns:
    df['region'] = df['region'].astype(str).str.strip()

    # 💡 [핵심 매핑 딕셔너리] 요청하신 치환 규칙을 1:1로 정확히 지정합니다.
    region_mapping = {
        "경기": "경기도",
        "충남": "충청남도",  
        "충북": "충청북도",  
        "경남": "경상남도",
        "경북": "경상북도",
        "전남": "전라남도",
        "인천": "인천광역시",
        "부산": "부산광역시",  
        "대구": "대구광역시",  
        "울산": "울산광역시",  
        "대전": "대전광역시",  
        "광주": "광주광역시"
    }

    print("치환 중...")
    
    # .replace() 기능을 사용하면 딕셔너리에 정의된 단어만 쏙쏙 골라 바꿉니다.
    # 정의되지 않은 값(예: 서울, 강원특별자치도 등)은 원래 상태 그대로 안전하게 유지됩니다.
    df['region'] = df['region'].replace(region_mapping)
    
    print("정제 완료")
    
    # 잘 바뀌었는지 고유값 요약 확인
    print("\n region 열에 남은 지역명 종류")
    print(list(df['region'].unique()))

else:
    print("'region' 컬럼을 찾을 수 없습니다. 이전 단계 코드가 잘 실행되었는지 확인해주세요.")

# 4. 최종 결과 저장
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"\n작업 완료")
print(f"'{OUTPUT_FILE}' 저장")