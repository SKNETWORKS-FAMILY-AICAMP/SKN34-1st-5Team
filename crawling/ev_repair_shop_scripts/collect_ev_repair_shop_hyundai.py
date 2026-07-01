import requests
import pandas as pd

API_URL = "https://www.car365.go.kr/ccpt/carlife/operate/selectElctyImprmnBzentyList.do"

# 일반 브라우저로 위장하기 위한 헤더 설정 (보안 차단 방지)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.car365.go.kr/ccpt/carlife/operate/elctyImprmnBzentyView.do",
    "X-Requested-With": "XMLHttpRequest"
}

# 3. 전체 조회를 위해 검색 조건을 '현대'로 설정
payload = {
    "mkrNm": "현대",        # 제조사
    "imprmnDtls": "",   # 정비범위
    "ctpvNm": "",       # 시도명
    "sggNm": "",        # 시군구명
    "srchGubun": "",    # 검색구분
    "srchText": ""      # 검색어
}

print("전기차 정비소 데이터 추출 시작")

try:
    # 비하인드 API 서버에 직접 요청을 보냅니다.
    response = requests.post(API_URL, data=payload, headers=headers)
    
    if response.status_code == 200:
        raw_data = response.json()
        
        if raw_data:
            df = pd.DataFrame(raw_data)
            
            column_mapping = {
                "imprmnBzentyNm": "업체명",
                "mkrNm": "제조사",
                "imprmnDtls": "정비범위",
                "telNo": "전화번호"
            }
            df = df.rename(columns=column_mapping)
            
            target_columns = ["업체명", "제조사", "정비범위", "전화번호"]
            
            # 엑셀에 들어갈 컬럼들이 데이터에 잘 존재하는지 검증 후 필터링
            available_cols = [col for col in target_columns if col in df.columns]
            final_df = df[available_cols]
            
            # 한글 깨짐 방지를 위해 utf-8-sig 사용
            output_file = "ev_repair_shops_clean.csv"
            final_df.to_csv(output_file, index=False, encoding="utf-8-sig")
            
            print(f"\n수집 완료")
            print(f"'{output_file}' 저장완료")
            
        else:
            print("서버 응답은 성공했으나 데이터 내용이 비어있습니다.")
    else:
        print(f"서버 접근 실패 (응답 코드: {response.status_code})")

except Exception as e:
    print(f"실행 중 오류 발생: {e}")