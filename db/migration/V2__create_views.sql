-- EV Purchase Support Information System View Definitions

-- 1. Electric Vehicle Detail
-- Usage: EV model info lookup (dashboard)

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
FROM      electric_vehicle AS ev
JOIN      manufacturer     AS m       ON ev.manufacturer_id       = m.id
LEFT JOIN charging_type    AS slow_ct ON ev.slow_charging_type_id = slow_ct.id
LEFT JOIN charging_type    AS fast_ct ON ev.fast_charging_type_id = fast_ct.id;


-- 2. Subsidy Detail
-- Usage: regional EV subsidy lookup (dashboard)

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
FROM      subsidy          AS s
JOIN      electric_vehicle AS ev ON s.electric_vehicle_id = ev.id
JOIN      manufacturer     AS m  ON ev.manufacturer_id    = m.id
JOIN      region           AS r  ON s.region_id           = r.id;


-- 3. EV Registration by Region
-- Usage: regional EV registration lookup, yearly trend chart (dashboard)

CREATE VIEW v_ev_registration_by_region AS
SELECT
    r.name    AS region_name,
    er.year,
    er.ev_count
FROM      ev_registration AS er
JOIN      region          AS r ON er.region_id = r.id;


-- 4. EV Adoption Rate by Region
-- Usage: EV adoption rate per population (dashboard)

CREATE VIEW v_adoption_rate_by_region AS
SELECT
    r.name           AS region_name,
    ea.adoption_rate
FROM      ev_adoption_rate AS ea
JOIN      region           AS r ON ea.region_id = r.id;


-- 5. Charging Station Count by Region
-- Usage: regional charging station count card, bar chart (dashboard)

CREATE VIEW v_charging_station_count_by_region AS
SELECT
    r.name       AS region_name,
    COUNT(cs.id) AS total_count
FROM      region           AS r
LEFT JOIN charging_station AS cs ON cs.region_id = r.id
GROUP BY  r.name;


-- 6. Repair Shop Count by Region
-- Usage: regional repair shop count card, bar chart (dashboard)

CREATE VIEW v_repair_shop_count_by_region AS
SELECT
    r.name       AS region_name,
    COUNT(rs.id) AS total_count
FROM      region      AS r
LEFT JOIN repair_shop AS rs ON rs.region_id = r.id
GROUP BY  r.name;


-- 7. Charging Station Map
-- Usage: map page charging station markers and list

CREATE VIEW v_charging_station_map AS
SELECT
    cs.id,
    cs.name,
    r.name  AS region_name,
    c.name  AS city_name,
    cs.latitude,
    cs.longitude,
    ct.name AS charging_type_name,
    cs.contact,
    cs.available_time
FROM      charging_station AS cs
JOIN      region           AS r  ON cs.region_id        = r.id
LEFT JOIN city             AS c  ON cs.city_id          = c.id
LEFT JOIN charging_type    AS ct ON cs.charging_type_id = ct.id;


-- 8. Repair Shop Map
-- Usage: map page repair shop markers and list

CREATE VIEW v_repair_shop_map AS
SELECT
    rs.id,
    rs.name,
    r.name   AS region_name,
    c.name   AS city_name,
    rs.latitude,
    rs.longitude,
    rst.name AS repair_shop_type_name,
    rs.contact,
    rs.available_time
FROM      repair_shop      AS rs
JOIN      region           AS r   ON rs.region_id           = r.id
LEFT JOIN city             AS c   ON rs.city_id             = c.id
LEFT JOIN repair_shop_type AS rst ON rs.repair_shop_type_id = rst.id;


-- 9. Region Stats Map
-- Usage: map page choropleth color by region

CREATE VIEW v_region_stats_map AS
SELECT
    r.name           AS region_name,
    er.year,
    er.ev_count,
    ea.adoption_rate
FROM      region           AS r
LEFT JOIN ev_registration  AS er ON er.region_id = r.id
LEFT JOIN ev_adoption_rate AS ea ON ea.region_id = r.id;


-- 10. City by Region
-- Usage: city list lookup by region (LocationService)

CREATE VIEW v_city_by_region AS
SELECT
    r.name AS region_name,
    c.name AS city_name
FROM      city   AS c
JOIN      region AS r ON c.region_id = r.id;


-- 11. FAQ Full
-- Usage: FAQ search and lookup (FAQ page)

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
