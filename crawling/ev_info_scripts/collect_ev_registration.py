from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# 1. 크롬 드라이버 설정 및 다나와 접속
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 다나와 신차 검색/목록 페이지
url = "https://auto.danawa.com/newcar/?listSortType=1&tab=all&rangeMinPrice=&rangeMaxPrice=&searchKeyword=&listCount=30&page=1&brandList=303,307&segmentList=C,PC1,PC2,PC3,PC4,PC5,RU2,RU3,RU5&attributeList=2|20|S" 
driver.get(url)
time.sleep(3) # 첫 페이지 로딩 대기

data = []
original_tab = driver.current_window_handle

print("다나와 자동차 상세 스펙 크롤링 시작")

try:
    # 앞서 검증 완료된 메인 목록의 차량 링크 태그 수집
    model_links = driver.find_elements(By.CSS_SELECTOR, ".list.modelList .name.sendGA")
    total_cars = len(model_links)
    print(f"분석된 수집 대상 차량: 총 {total_cars}대\n")
    
    for index in range(total_cars):
        # StaleElement(태그 만료) 에러 방지를 위해 루프마다 목록 실시간 갱신
        current_links = driver.find_elements(By.CSS_SELECTOR, ".list.modelList .name.sendGA")
        target_link = current_links[index]
        
        model_name_log = target_link.text.strip()
        print(f"[{index + 1}/{total_cars}] '{model_name_log}' 상세 페이지 진입 중...")
        
        try:
            # ① 컨트롤 클릭 조합으로 새 탭 열기
            webdriver.ActionChains(driver).key_down(Keys.CONTROL).click(target_link).key_up(Keys.CONTROL).perform()
            time.sleep(2) # 새 탭 오픈 대기
            
            # ② 제어권을 새로 열린 상세 페이지 탭(가장 오른쪽)으로 전환
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3.5) # 상세 페이지 내부 요소들이 완전히 로딩될 때까지 넉넉히 대기
            
            # -------------------------------------------------------------
            
            grid_main = driver.find_element(By.CLASS_NAME, "gridMain")
            
            # 제조사 추출
            maker_li = grid_main.find_elements(By.CSS_SELECTOR, ".list > li")[2]
            maker = maker_li.find_element(By.TAG_NAME, "button").text.strip()
            
            # 모델명 추출
            model_name = grid_main.find_element(By.CSS_SELECTOR, ".info .title").text.strip()
            
            # 세부 트림 목록 추출
            try:
                target_ul = grid_main.find_element(By.CSS_SELECTOR, ".price_contents.on .price_list ul.on")
                trims = target_ul.find_elements(By.TAG_NAME, "li")
                
                for trim in trims:
                    try:
                        trim_name = trim.find_element(By.CSS_SELECTOR, ".item.name label").text.strip()
                        engine_row = trim.find_element(By.CLASS_NAME, "item.engine").text.strip()
                        engine = engine_row.replace('km','')
                        mileage_row = trim.find_element(By.CLASS_NAME, "mileage").text.strip()
                        mileage = mileage_row.replace('㎞/kWh','')
                        price_row = trim.find_element(By.CLASS_NAME, "price").text.strip()
                        price = price_row.replace('만 원', '').replace(',', '')
                        
                        # 데이터 적재 및 출력
                        print(f"제조사: {maker} | 모델명: {model_name} | 트림: {trim_name} | 1회충전주행거리: {engine} | 복합전비: {mileage} | 가격: {price}")
                        data.append([maker, model_name, trim_name, engine, mileage, price])
                        
                    except Exception as e:
                        # 리스트 내부 항목 중 빈 칸이나 레이아웃 예외 처리
                        continue
                        
            except Exception as e:
                print(f"활성화된 트림 스펙 영역(.price_contents.on)을 찾지 못해 패스")
            
            # -------------------------------------------------------------
            # ③ 한 차량의 수집이 끝나면 상세 탭을 닫고 원래 목록으로 복귀
            # -------------------------------------------------------------
            driver.close()
            driver.switch_to.window(original_tab)
            time.sleep(1) # 원래 화면 복귀 후 안전을 위한 짧은 대기
            
        except Exception as e:
            print(f"   ❌ [{model_name_log}] 처리 중 에러 발생, 다음 차량으로 넘어갑니다.")
            # 에러 발생 시 시선이 새 탭에 갇혀 꼬이는 것을 막는 안전장치
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(original_tab)
            time.sleep(1)
            continue

except Exception as e:
    print(f"치명적인 루프 오류 발생: {e}")

# 2. 브라우저 완전히 종료
driver.quit()
print("탐색 종료")

# 3. 데이터프레임 변환 및 CSV 최종 저장
if data:
    df = pd.DataFrame(data, columns=['제조사', '모델명', '세부트림', '1회충전주행거리', '복합전비', '가격'])
    df.to_csv("danawa_final_ev_data.csv", index=False, encoding="utf-8")
    print(f"🎉 전량 데이터 수집 완료! 총 {len(data)}개의 데이터가 'danawa_final_ev_data.csv' 파일로 저장되었습니다.")
else:
    print("❌ 수집된 데이터가 없습니다. 상세 페이지 내부의 클래스명을 다시 한번 점검해 주세요.")