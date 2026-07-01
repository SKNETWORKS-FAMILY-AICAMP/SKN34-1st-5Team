import pandas as pd

df1 = pd.read_csv("hyundai_shops.csv", encoding="utf-8-sig")  # 첫 번째 파일
df2 = pd.read_csv("kia_shops.csv", encoding="utf-8-sig")      # 두 번째 파일

# 두 파일 위아래로 하나로 합치기
df = pd.concat([df1, df2], ignore_index=True)

print(f"파일({len(df1)}건) + ({len(df2)}건) = 총 {len(df)}건 통합 완료")


def fix_shop_name(row):
    maker = str(row['제조사']).strip()
    name = str(row['업체명']).strip()
    if "현대" in maker and "현대" not in name:
        return f"{name} 블루핸즈"
    elif "기아" in maker and "기아" not in name and "오토큐" not in name:
        return f"{name} 기아 오토큐"
    return name

df['업체명'] = df.apply(fix_shop_name, axis=1)

# 통합된 최종 결과 저장
df.to_csv("ev_repair_shops_fixed_all.csv", index=False, encoding="utf-8-sig")
print("두 파일의 모든 데이터가 보정되어 'ev_repair_shops_fixed_all.csv'로 통합 저장되었습니다.")