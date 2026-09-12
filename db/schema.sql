DROP TABLE IF EXISTS mart_hourly_profile;
DROP TABLE IF EXISTS mart_region_monthly;
DROP TABLE IF EXISTS dim_station_info;
DROP TABLE IF EXISTS dim_region_mapping;
DROP TABLE IF EXISTS raw_living_pop;
DROP TABLE IF EXISTS raw_subway_time;

-- 1. 원본 계층 
CREATE TABLE raw_subway_time (
    stats_date VARCHAR(10),
    line_num VARCHAR(50),
    station_name VARCHAR(100),
    hour_slot VARCHAR(20),
    ride_count INT,
    alight_count INT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_raw_subway ON raw_subway_time(line_num, station_name);

CREATE TABLE raw_living_pop (
    region_code VARCHAR(10),
    base_date VARCHAR(10),
    hour INT,
    gender VARCHAR(10),
    age_band VARCHAR(20),
    pop_cnt DOUBLE,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_raw_pop ON raw_living_pop(region_code, base_date);

-- 2. 차원 테이블 
CREATE TABLE dim_region_mapping (
    region_code VARCHAR(10) PRIMARY KEY,
    signgu_name VARCHAR(50),
    dong_name VARCHAR(50)
);

CREATE TABLE dim_station_info (
    station_name VARCHAR(100),
    line_num VARCHAR(50),
    region_code VARCHAR(10),
    PRIMARY KEY (station_name, line_num)
);

-- 3. 마트 계층 
CREATE TABLE mart_region_monthly (
    region_code VARCHAR(10),
    base_ym VARCHAR(7),
    avg_daily_pop DOUBLE,
    peak_hour INT,
    weekday_pop DOUBLE,
    weekend_pop DOUBLE,
    resident_pop INT,
    activity_ratio DOUBLE,
    store_count INT,
    pop_per_store DOUBLE,
    mom_change DOUBLE,
    PRIMARY KEY (region_code, base_ym)
);

CREATE TABLE mart_hourly_profile (
    region_code VARCHAR(10),
    base_ym VARCHAR(7),
    hour INT,
    age_band VARCHAR(20),
    avg_pop DOUBLE,
    PRIMARY KEY (region_code, base_ym, hour, age_band)
);