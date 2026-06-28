"""
KGM(KG모빌리티) FAQ 수집 스크립트
- REST API 사용: web.kg-mobility.com
- 목록: getFaqContentList.do (117건, bbNo + title + categoryNm)
- 상세: getFaqContentDetail.do?bbNo=<bbNo> (HTML content → 텍스트 변환)
"""

import csv
import re
import time
from bs4 import BeautifulSoup
from datetime import date
from pathlib import Path

import requests

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "faq"
OUTPUT_DIR.mkdir(exist_ok=True)

TODAY = date.today().isoformat()
SOURCE_URL = "https://www.kg-mobility.com/sr/online-center/faq/detail?searchWord=&categoryCd=300"
FIELDS = ["company", "category", "sub_category", "question", "answer", "collected_at", "source_url"]

_LIST_API = "https://web.kg-mobility.com/app/customer/getFaqContentList.do"
_DETAIL_API = "https://web.kg-mobility.com/app/customer/getFaqContentDetail.do"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": SOURCE_URL,
}


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def collect_kgm() -> list[dict]:
    # 1) 목록 전체 수집
    r = requests.get(
        _LIST_API,
        params={"pageIdx": 1, "rowsPerPage": 300, "searchWord": "", "categoryCd": ""},
        headers=_HEADERS,
        timeout=15,
    )
    data = r.json()
    if data.get("code") != "0000":
        raise RuntimeError(f"목록 API 오류: {data}")

    items = data["body"]["list"]
    print(f"  목록 {len(items)}건 수신")

    rows: list[dict] = []
    for i, item in enumerate(items):
        bb_no = item["bbNo"]
        category = item.get("categoryNm", "")
        title = item.get("title", "").strip()

        # 2) 상세 API로 답변 수집
        dr = requests.get(_DETAIL_API, params={"bbNo": bb_no}, headers=_HEADERS, timeout=10)
        detail = dr.json()
        if detail.get("code") != "0000":
            print(f"  [{i+1}/{len(items)}] bbNo={bb_no} 상세 오류, 건너뜀")
            time.sleep(0.3)
            continue

        content_html = detail["body"]["info"].get("content") or ""
        answer = html_to_text(content_html)

        rows.append({
            "company": "KGM",
            "category": category,
            "sub_category": "",
            "question": title,
            "answer": answer,
            "collected_at": TODAY,
            "source_url": SOURCE_URL,
        })

        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{len(items)}] 수집 중...")
        time.sleep(0.2)

    return rows


def main() -> None:
    print("[KGM] FAQ 수집 중...")
    rows = collect_kgm()
    print(f"  → {len(rows)}건 수집 완료")

    # kgm_faq.csv 저장
    out_path = OUTPUT_DIR / "kgm_faq.csv"
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  저장: {out_path} ({len(rows)}건)")

    # all_faq.csv 업데이트
    all_path = OUTPUT_DIR / "all_faq.csv"
    existing: list[dict] = []
    if all_path.exists():
        with open(all_path, "r", encoding="utf-8-sig") as f:
            existing = list(csv.DictReader(f))
        existing = [r for r in existing if r.get("company") != "KGM"]

    all_rows = existing + rows
    with open(all_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"  all_faq.csv → {len(all_rows)}건")


if __name__ == "__main__":
    main()
