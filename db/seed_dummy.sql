INSERT INTO dim_region_mapping (region_code, signgu_name, dong_name) VALUES 
('11110515', '종로구', '청운효자동'),
('11560540', '영등포구', '여의동'),
('11680610', '강남구', '대치1동');

INSERT INTO raw_living_pop (region_code, base_date, hour, gender, age_band, pop_cnt) VALUES 
('11110515', '2026-06-01', 8, 'M', '20s', 15000.5),
('11110515', '2026-06-01', 18, 'F', '30s', 18200.0),
('11560540', '2026-06-01', 8, 'M', '30s', 45000.0),
('11680610', '2026-06-01', 8, 'F', '20s', 38000.0);

INSERT INTO raw_subway_time (stats_date, line_num, station_name, hour_slot, ride_count, alight_count) VALUES 
('2026-06-01', '3호선', '경복궁', '08', 3000, 12000),
('2026-06-01', '9호선', '여의도', '08', 2000, 25000),
('2026-06-01', '2호선', '선릉', '08', 5000, 30000);