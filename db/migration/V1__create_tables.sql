-- transactional: false
-- EV Purchase Support Information System DB Schema

-- Lookup Tables

CREATE TABLE IF NOT EXISTS manufacturer (
    id   INT         NOT NULL AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS charging_type (
    id   INT         NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS repair_shop_type (
    id   INT         NOT NULL AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS region (
    id   INT         NOT NULL AUTO_INCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS city (
    id        INT         NOT NULL AUTO_INCREMENT,
    region_id INT         NOT NULL,
    code      VARCHAR(20) NOT NULL UNIQUE,
    name      VARCHAR(30) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (region_id) REFERENCES region (id)
);

CREATE TABLE IF NOT EXISTS faq_category (
    id       INT         NOT NULL AUTO_INCREMENT,
    category VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);

-- Electric Vehicle

CREATE TABLE IF NOT EXISTS electric_vehicle (
    id                    INT         NOT NULL AUTO_INCREMENT,
    manufacturer_id       INT         NOT NULL,
    model_name            VARCHAR(50) NOT NULL,
    trim_name             VARCHAR(50),
    price                 INT         NOT NULL,
    driving_range         FLOAT,
    efficiency            FLOAT,
    slow_charging_type_id INT,
    fast_charging_type_id INT,
    PRIMARY KEY (id),
    UNIQUE KEY uq_vehicle (manufacturer_id, model_name, trim_name),
    FOREIGN KEY (manufacturer_id)       REFERENCES manufacturer  (id),
    FOREIGN KEY (slow_charging_type_id) REFERENCES charging_type (id),
    FOREIGN KEY (fast_charging_type_id) REFERENCES charging_type (id)
);

-- Subsidy

CREATE TABLE IF NOT EXISTS subsidy (
    id                          INT NOT NULL AUTO_INCREMENT,
    electric_vehicle_id         INT NOT NULL,
    region_id                   INT NOT NULL,
    year                        INT NOT NULL,
    national_subsidy            INT,
    local_subsidy               INT,
    national_conversion_subsidy INT,
    local_conversion_subsidy    INT,
    PRIMARY KEY (id),
    UNIQUE KEY uq_subsidy (electric_vehicle_id, region_id, year),
    FOREIGN KEY (electric_vehicle_id) REFERENCES electric_vehicle (id),
    FOREIGN KEY (region_id)           REFERENCES region           (id)
);

-- Charging Station

CREATE TABLE IF NOT EXISTS charging_station (
    id               INT          NOT NULL AUTO_INCREMENT,
    name             VARCHAR(100) NOT NULL,
    region_id        INT          NOT NULL,
    city_id          INT,
    address          VARCHAR(255),
    latitude         FLOAT,
    longitude        FLOAT,
    contact          VARCHAR(100),
    available_time   VARCHAR(100),
    charging_type_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY (region_id)        REFERENCES region        (id),
    FOREIGN KEY (city_id)          REFERENCES city          (id),
    FOREIGN KEY (charging_type_id) REFERENCES charging_type (id)
);

-- Repair Shop

CREATE TABLE IF NOT EXISTS repair_shop (
    id                  INT          NOT NULL AUTO_INCREMENT,
    name                VARCHAR(100) NOT NULL,
    region_id           INT          NOT NULL,
    city_id             INT,
    address             VARCHAR(255),
    latitude            FLOAT,
    longitude           FLOAT,
    available_time      VARCHAR(100),
    contact             VARCHAR(100),
    repair_shop_type_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY (region_id)           REFERENCES region           (id),
    FOREIGN KEY (city_id)             REFERENCES city             (id),
    FOREIGN KEY (repair_shop_type_id) REFERENCES repair_shop_type (id)
);

-- FAQ

CREATE TABLE IF NOT EXISTS faq (
    id              INT  NOT NULL AUTO_INCREMENT,
    manufacturer_id INT  NOT NULL,
    faq_category_id INT,
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    source_url      VARCHAR(500),
    PRIMARY KEY (id),
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturer (id),
    FOREIGN KEY (faq_category_id) REFERENCES faq_category (id)
);

-- EV Registration by Region

CREATE TABLE IF NOT EXISTS ev_registration (
    id        INT NOT NULL AUTO_INCREMENT,
    region_id INT NOT NULL,
    year      INT NOT NULL,
    ev_count  INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_ev_registration (region_id, year),
    FOREIGN KEY (region_id) REFERENCES region (id)
);

-- EV Adoption Rate by Region

CREATE TABLE IF NOT EXISTS ev_adoption_rate (
    id            INT   NOT NULL AUTO_INCREMENT,
    region_id     INT   NOT NULL,
    adoption_rate FLOAT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (region_id) REFERENCES region (id)
);
