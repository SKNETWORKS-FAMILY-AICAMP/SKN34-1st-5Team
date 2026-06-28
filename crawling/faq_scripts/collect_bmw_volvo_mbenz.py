"""
볼보코리아 + BMW코리아 + 메르세데스-벤츠코리아 FAQ 수집 스크립트
- 볼보: volvocars.com/kr/support/ → topic → subtopic → article(title+ingress)
- BMW:  bmw.co.kr/kr/s/ → Salesforce 포털 innerText 파싱
- 메르세데스-벤츠: mercedes-benz.co.kr MBMK FAQ → WB7-ACCORDION shadow DOM innerText 파싱
"""

import csv
import re
import time
from bs4 import BeautifulSoup
from datetime import date
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "faq"
OUTPUT_DIR.mkdir(exist_ok=True)

TODAY = date.today().isoformat()
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
VOLVO_BASE = "https://www.volvocars.com"
FIELDS = ["company", "category", "sub_category", "question", "answer", "collected_at", "source_url"]


def make_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"user-agent={UA}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=opts)


# ─────────────────────────────────────────────────────────────
#  볼보 수집
# ─────────────────────────────────────────────────────────────

def _get_support_links(drv: webdriver.Chrome, url: str) -> list[dict]:
    drv.get(url)
    time.sleep(6)
    soup = BeautifulSoup(drv.page_source, "lxml")
    result = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/kr/support/topic/" not in href:
            continue
        segs = [s for s in href.split("/") if s]
        depth = len(segs) - 3  # 0=root, 1=topic, 2=subtopic, 3=article
        text = a.get_text(" ", strip=True)
        result.append({"text": text, "href": href, "depth": depth})
    return result


def _extract_articles(drv: webdriver.Chrome) -> tuple[list[str], dict[str, str]]:
    """현재 페이지에서 article URL→title+ingress 추출 (볼보 sub-topic 페이지용)."""
    soup = BeautifulSoup(drv.page_source, "lxml")
    body = soup.body.get_text("\n", strip=True) if soup.body else ""
    lines = [l.strip() for l in body.split("\n") if l.strip() and len(l.strip()) > 3]

    # 쿠키 배너 이전까지만 사용
    clean: list[str] = []
    for l in lines:
        if "당사는 콘텐츠 및 광고를 개인화" in l or "개인 정보 보호 기본 설정 센터" in l:
            break
        clean.append(l)

    # article 링크 (3-depth: topic/subtopic/article)
    art_links: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        segs = [s for s in href.split("/") if s]
        if len(segs) == 6 and segs[2] == "topic":
            art_links[href] = a.get_text(" ", strip=True)

    return clean, art_links


def collect_volvo(drv: webdriver.Chrome) -> list[dict]:
    rows: list[dict] = []
    seen_url: set[str] = set()

    # 메인 지원 페이지에서 topic 목록 수집
    drv.get(f"{VOLVO_BASE}/kr/support/")
    time.sleep(6)
    soup_main = BeautifulSoup(drv.page_source, "lxml")
    topic_links: dict[str, str] = {}
    for a in soup_main.find_all("a", href=True):
        href = a["href"]
        if "/kr/support/topic/" not in href:
            continue
        segs = [s for s in href.split("/") if s]
        if len(segs) == 4:
            txt = a.get_text(strip=True)
            if txt and "보기" not in txt:
                topic_links[href] = txt

    for topic_href, topic_name in topic_links.items():
        # 카테고리 이름 정리
        cat_clean = topic_name.split("\n")[0].strip()
        if cat_clean.startswith("Volvo Cars app"):
            cat_clean = "Volvo Cars 앱"

        topic_url = f"{VOLVO_BASE}{topic_href}"
        links = _get_support_links(drv, topic_url)
        subtopic_links = [d for d in links if d["depth"] == 2]

        for st in subtopic_links:
            st_url = f"{VOLVO_BASE}{st['href']}"
            if st_url in seen_url:
                continue

            drv.get(st_url)
            time.sleep(5)
            sub_name = drv.title.split("|")[0].strip()

            clean_lines, art_links = _extract_articles(drv)
            article_urls = [f"{VOLVO_BASE}{h}" for h in art_links.keys()]

            # body에서 title+ingress 쌍 추출 (alternating lines)
            pairs: list[tuple[str, str]] = []
            i = 0
            while i < len(clean_lines) - 1:
                t = clean_lines[i]
                a_text = clean_lines[i + 1]
                if len(t) > 5 and len(a_text) > 5 and t != a_text:
                    pairs.append((t, a_text))
                    i += 2
                else:
                    i += 1

            for idx, art_url in enumerate(article_urls):
                if art_url in seen_url:
                    continue
                seen_url.add(art_url)

                q, a_text = pairs[idx] if idx < len(pairs) else ("", "")
                if not q or len(q) < 4:
                    continue
                # 탐색 breadcrumb 제거 (Q가 sub_name이나 cat_clean과 동일)
                if q in (sub_name, cat_clean, topic_name):
                    continue
                # URL fragment가 질문에 들어간 경우 제거
                if "/kr/support/topic/" in q:
                    continue

                rows.append({
                    "company": "볼보",
                    "category": cat_clean,
                    "sub_category": sub_name,
                    "question": q,
                    "answer": a_text,
                    "source_url": art_url,
                    "collected_at": TODAY,
                })

    return rows


# ─────────────────────────────────────────────────────────────
#  BMW 수집
# ─────────────────────────────────────────────────────────────

def collect_bmw(drv: webdriver.Chrome) -> list[dict]:
    """BMW FAQ 포털(Salesforce) — '도움말 더 보기' 반복 클릭으로 전체 수집."""
    url = "https://www.bmw.co.kr/kr/s/?language=ko"
    drv.get(url)
    time.sleep(20)

    # "도움말 더 보기" 버튼이 사라질 때까지 반복 클릭 (find_element 실패 시 루프 종료)
    while True:
        try:
            btn = drv.find_element(By.XPATH, "//button[contains(text(),'도움말 더 보기')]")
            drv.execute_script("arguments[0].click();", btn)
            time.sleep(5)
        except Exception:
            break

    inner_text: str = drv.execute_script("return document.body.innerText") or ""
    lines = [l.strip() for l in inner_text.split("\n") if l.strip()]
    rows: list[dict] = []
    seen: set[str] = set()

    # 구조: [조회수] → [질문] → [답변...] → 전체 도움말 보기
    for i, line in enumerate(lines):
        if line == "전체 도움말 보기" and i >= 2:
            q = re.sub(r"^\d[\d,]*\s*", "", lines[i - 2]).strip()
            a = lines[i - 1].strip()
            if re.match(r"^\d[\d,]+$", lines[i - 2]):
                continue
            if q and len(q) > 5 and q not in seen:
                seen.add(q)
                rows.append({
                    "company": "BMW",
                    "category": "FAQ",
                    "sub_category": "",
                    "question": q,
                    "answer": a,
                    "source_url": url,
                    "collected_at": TODAY,
                })

    return rows


# ─────────────────────────────────────────────────────────────
#  실행 진입점
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
#  메르세데스-벤츠 수집
# ─────────────────────────────────────────────────────────────

_MBENZ_CATEGORY_RE = re.compile(r'^[IVXivxⅠⅡⅢⅣⅤ]+\.')
_MBENZ_END_MARKERS = {"회원 가입하고 소식 받기", "Mercedes-Benz 계정을 등록하고"}

def collect_mbenz(drv: webdriver.Chrome) -> list[dict]:
    """메르세데스-벤츠 MBMK FAQ — WB7-ACCORDION shadow DOM innerText 파싱.

    Shadow DOM 특성상 Q1(첫 번째 질문)이 모든 항목 직전에 노이즈로 삽입됨.
    Q1 직전 줄이 실제 질문이므로 Q1을 구분자로 활용.
    """
    url = "https://www.mercedes-benz.co.kr/passengercars/buy/mbmk/help/help-faq.html"
    drv.get(url)
    time.sleep(20)

    inner: str = drv.execute_script("return document.body.innerText") or ""
    lines = [l.strip() for l in inner.split("\n") if l.strip()]

    faq_start = next((i for i, l in enumerate(lines) if l == "FAQs"), None)
    if faq_start is None:
        return []
    faq_lines = lines[faq_start + 1:]

    # 첫 번째 질문(= 노이즈 기준값) 탐색
    q1_text: str = ""
    for l in faq_lines:
        if _MBENZ_CATEGORY_RE.match(l):
            continue
        q1_text = l
        break
    if not q1_text:
        return []

    rows: list[dict] = []
    current_cat = ""
    q_current: str | None = None
    q_cat = ""
    a_lines: list[str] = []
    last_non_cat: str | None = None

    def flush_row() -> None:
        nonlocal q_current, q_cat, a_lines
        if q_current and a_lines:
            rows.append({
                "company": "메르세데스-벤츠",
                "category": q_cat,
                "sub_category": "",
                "question": q_current,
                "answer": " ".join(a_lines),
                "collected_at": TODAY,
                "source_url": url,
            })
        q_current = None
        q_cat = ""
        a_lines = []

    for line in faq_lines:
        if any(line.startswith(m) for m in _MBENZ_END_MARKERS):
            break
        if _MBENZ_CATEGORY_RE.match(line):
            current_cat = line
            continue
        if line == q1_text:
            if last_non_cat is not None:
                if a_lines and a_lines[-1] == last_non_cat:
                    a_lines.pop()
                next_q, next_q_cat = last_non_cat, current_cat
                flush_row()
                q_current, q_cat = next_q, next_q_cat
            elif q_current is None:
                q_current, q_cat = q1_text, current_cat
            last_non_cat = None
            continue
        if q_current is not None:
            a_lines.append(line)
        last_non_cat = line

    flush_row()
    return rows


def main() -> None:
    drv = make_driver()
    try:
        print("[볼보] 수집 중...")
        volvo_rows = collect_volvo(drv)
        print(f"  → {len(volvo_rows)}건")

        print("[BMW] 수집 중...")
        bmw_rows = collect_bmw(drv)
        print(f"  → {len(bmw_rows)}건")

        print("[메르세데스-벤츠] 수집 중...")
        mbenz_rows = collect_mbenz(drv)
        print(f"  → {len(mbenz_rows)}건")
    finally:
        drv.quit()

    # 개별 파일 저장
    for fname, data in [
        ("volvo_faq.csv", volvo_rows),
        ("bmw_faq.csv", bmw_rows),
        ("mbenz_faq.csv", mbenz_rows),
    ]:
        out_path = OUTPUT_DIR / fname
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(data)
        print(f"  저장: {out_path}")

    # all_faq.csv 병합
    all_path = OUTPUT_DIR / "all_faq.csv"
    existing: list[dict] = []
    if all_path.exists():
        with open(all_path, encoding="utf-8-sig") as f:
            existing = [r for r in csv.DictReader(f)
                        if r.get("company") not in {"볼보", "BMW", "메르세데스-벤츠"}]

    combined = existing + volvo_rows + bmw_rows + mbenz_rows
    with open(all_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(combined)

    from collections import Counter
    counts = Counter(r["company"] for r in combined)
    print(f"\n[all_faq.csv] 총 {len(combined)}건")
    for c, n in sorted(counts.items()):
        print(f"  {c}: {n}건")


if __name__ == "__main__":
    main()
