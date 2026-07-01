-- ============================================================
--  전기차 구매 지원 정보 시스템 뷰 정의
-- ============================================================

-- ── 1. 전기차 차종 상세 ──────────────────────────────────────
--  용도: 전기차 차종 정보 조회 (대시보드)
--  제조사명, 모델명, 트림명, 가격, 주행거리, 전비, 충전타입명

CREATE VIEW v_electric_vehicle_detail AS
SELECT
    ev.id,
    m.name                AS manufacturer_name,
    ev.model_name,
    ev.trim_name,
    ev.price,
    ev.driving_range,
    ev.efficiency,
    slow_ct.name          AS slow_charging_type_name,
    fast_ct.name          AS fast_charging_type_name
FROM       electric_vehicle AS ev
JOIN       manufacturer     AS m       ON ev.manufacturer_id       = m.id
LEFT JOIN  charging_type    AS slow_ct ON ev.slow_charging_type_id = slow_ct.id
LEFT JOIN  charging_type    AS fast_ct ON ev.fast_charging_type_id = fast_ct.id;


-- ── 2. 보조금 상세 ───────────────────────────────────────────
--  용도: 지역별 전기차 보조금 조회 (대시보드)
--  제조사명, 모델명, 트림명, 시도명, 연도, 국비/지방비/전환보조금

CREATE VIEW v_subsidy_detail AS
SELECT
    m.name                         AS manufacturer_name,
    ev.model_name,
    ev.trim_name,
    r.name                         AS region_name,
    s.year,
    s.national_subsidy,
    s.local_subsidy,
    s.national_conversion_subsidy,
    s.local_conversion_subsidy
FROM      subsidy           AS s
JOIN      electric_vehicle  AS ev ON s.electric_vehicle_id = ev.id
JOIN      manufacturer      AS m  ON ev.manufacturer_id    = m.id
JOIN      region            AS r  ON s.region_id           = r.id;


-- ── 3. 시도별 전기차 등록 현황 ──────────────────────────────
--  용도: 지역별 전기차 등록 현황 조회, 연도별 추이 차트 (대시보드)
--  시도명, 연도, 등록대수

CREATE VIEW v_ev_registration_by_region AS
SELECT
    r.name    AS region_name,
    er.year,
    er.ev_count
FROM      ev_registration AS er
JOIN      region          AS r  ON er.region_id = r.id;


-- ── 4. 시도별 전기차 보급률 ─────────────────────────────────
--  용도: 인구 대비 전기차 보급률 조회 (대시보드)
--  시도명, 보급률

CREATE VIEW v_adoption_rate_by_region AS
SELECT
    r.name           AS region_name,
    ea.adoption_rate
FROM      ev_adoption_rate AS ea
JOIN      region           AS r  ON ea.region_id = r.id;


-- ── 5. 시도별 충전소 수 집계 ────────────────────────────────
--  용도: 지역별 충전소 현황 수치 카드, 막대차트 (대시보드)
--  시도명, 충전소 총 수

CREATE VIEW v_charging_station_count_by_region AS
SELECT
    r.name       AS region_name,
    COUNT(cs.id) AS total_count
FROM      region           AS r
LEFT JOIN charging_station AS cs ON cs.region_id = r.id
GROUP BY  r.name;


-- ── 6. 시도별 정비소 수 집계 ────────────────────────────────
--  용도: 지역별 정비소 현황 수치 카드, 막대차트 (대시보드)
--  시도명, 정비소 총 수

CREATE VIEW v_repair_shop_count_by_region AS
SELECT
    r.name       AS region_name,
    COUNT(rs.id) AS total_count
FROM      region       AS r
LEFT JOIN repair_shop  AS rs ON rs.region_id = r.id
GROUP BY  r.name;


-- ── 7. 충전소 지도 마커 ──────────────────────────────────────
--  용도: 지도 페이지 충전소 마커 표시 및 목록 조회
--  충전소명, 시도명, 시군구명, 위도, 경도, 충전타입명, 운영시간, 연락처

CREATE VIEW v_charging_station_map AS
SELECT
    cs.id,
    cs.name,
    r.name               AS region_name,
    c.name               AS city_name,
    cs.latitude,
    cs.longitude,
    ct.name              AS charging_type_name,
    cs.contact,
    cs.start_time,
    cs.close_time
FROM      charging_station AS cs
JOIN      region            AS r  ON cs.region_id        = r.id
LEFT JOIN city              AS c  ON cs.city_id          = c.id
LEFT JOIN charging_type     AS ct ON cs.charging_type_id = ct.id;


-- ── 8. 정비소 지도 마커 ──────────────────────────────────────
--  용도: 지도 페이지 정비소 마커 표시 및 목록 조회
--  정비소명, 시도명, 시군구명, 위도, 경도, 정비소유형명, 운영시간, 연락처

CREATE VIEW v_repair_shop_map AS
SELECT
    rs.id,
    rs.name,
    r.name               AS region_name,
    c.name               AS city_name,
    rs.latitude,
    rs.longitude,
    rst.name             AS repair_shop_type_name,
    rs.contact,
    rs.start_time,
    rs.close_time
FROM      repair_shop       AS rs
JOIN      region            AS r   ON rs.region_id           = r.id
LEFT JOIN city              AS c   ON rs.city_id             = c.id
LEFT JOIN repair_shop_type  AS rst ON rs.repair_shop_type_id = rst.id;


-- ── 9. 시도별 통계 (지도 색상용) ────────────────────────────
--  용도: 지도 페이지 지역별 choropleth 색상 표현
--  시도명, 연도, 등록대수, 보급률

CREATE VIEW v_region_stats_map AS
SELECT
    r.name           AS region_name,
    er.year,
    er.ev_count,
    ea.adoption_rate
FROM      region           AS r
LEFT JOIN ev_registration  AS er ON er.region_id = r.id
LEFT JOIN ev_adoption_rate AS ea ON ea.region_id = r.id;


-- ── 10. 시도별 시/군/구 목록 ──────────────────────────────────
--  용도: 시도에 속한 시/군/구 목록 조회 (LocationService)
--  시도명, 시/군/구명

CREATE VIEW v_city_by_region AS
SELECT
    r.name AS region_name,
    c.name AS city_name
FROM      city   AS c
JOIN      region AS r ON c.region_id = r.id;


-- ── 11. FAQ 통합 ─────────────────────────────────────────────
--  용도: FAQ 검색 및 조회 (FAQ 페이지)
--  제조사명, 카테고리명, 질문, 답변, 출처 URL

CREATE VIEW v_faq_full AS
SELECT
    f.id,
    m.name           AS manufacturer_name,
    fc.category      AS faq_category,
    f.question,
    f.answer,
    f.source_url
FROM      faq          AS f
JOIN      manufacturer AS m  ON f.manufacturer_id = m.id
LEFT JOIN faq_category AS fc ON f.faq_category_id = fc.id;
