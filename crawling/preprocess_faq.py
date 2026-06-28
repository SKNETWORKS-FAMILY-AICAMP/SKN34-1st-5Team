# -*- coding: utf-8 -*-
"""
FAQ 데이터 전처리 스크립트
- 짧은 질문/답변 제거
- 볼보 Q/A 뒤바뀜 오류 제거 (답변이 카테고리 제목으로 들어간 케이스)
- 중복 질문 제거
"""
import csv
from pathlib import Path
from collections import Counter

INPUT  = Path(__file__).parent.parent / "data" / "faq" / "all_faq.csv"
OUTPUT = Path(__file__).parent.parent / "data" / "faq" / "preprocessing_faq.csv"

rows = list(csv.DictReader(open(INPUT, encoding="utf-8-sig")))
print(f"원본: {len(rows)}건")

# ── 1. 너무 짧은 질문/답변 제거 ──────────────────────────────────────────────
# 볼보는 답변이 30자 미만이면 카테고리명이 잘못 파싱된 케이스
before = len(rows)
cleaned = []
for r in rows:
    q = r["question"].strip()
    a = r["answer"].strip()
    if r["company"] == "볼보":
        if len(q) < 10 or len(a) < 30:
            continue
    else:
        if len(q) < 10 or len(a) < 10:
            continue
    cleaned.append(r)
rows = cleaned
print(f"짧은 Q/A 제거: {before - len(rows)}건 → {len(rows)}건")

# ── 2. 볼보 Q/A 뒤바뀜 제거 ─────────────────────────────────────────────────
# 질문이 본문 문장(>80자)이고 답변이 짧은 제목(<40자)인 경우 → 파싱 오류
before = len(rows)
volvo_rows, other_rows = [], []
for r in rows:
    (volvo_rows if r["company"] == "볼보" else other_rows).append(r)

volvo_clean = [
    r for r in volvo_rows
    if not (len(r["question"].strip()) > 80 and len(r["answer"].strip()) < 40)
]
rows = other_rows + volvo_clean
print(f"볼보 Q/A 뒤바뀜 제거: {before - len(rows)}건 → {len(rows)}건")

# ── 3. 중복 질문 제거 (question 기준, 첫 번째 유지) ──────────────────────────
before = len(rows)
seen = set()
deduped = []
for r in rows:
    key = r["question"].strip()
    if key not in seen:
        seen.add(key)
        deduped.append(r)
rows = deduped
print(f"중복 질문 제거: {before - len(rows)}건 → {len(rows)}건")

# ── 4. 줄바꿈 정규화 (필드 내 \n → 공백, 연속 공백 정리) ───────────────────
import re
for r in rows:
    for f in ("question", "answer"):
        r[f] = re.sub(r'\s*\n\s*', ' ', r[f]).strip()

# ── 저장 ────────────────────────────────────────────────────────────────────
fields = list(rows[0].keys())
with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n저장 완료: {OUTPUT.name} ({len(rows)}건)")

print("\n=== 최종 회사별 건수 ===")
for company, cnt in Counter(r["company"] for r in rows).most_common():
    print(f"  {company}: {cnt}건")
