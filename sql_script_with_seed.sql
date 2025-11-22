-- ============================================================================
-- FIXED COMPLETE DATABASE SETUP & SEEDING SCRIPT
-- Platform: PostgreSQL (supabasenDB)
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. CLEANUP
-- ============================================================================

DROP TABLE IF EXISTS "reimbursements" CASCADE;
DROP TABLE IF EXISTS "hotel_bookings" CASCADE;
DROP TABLE IF EXISTS "flight_bookings" CASCADE;
DROP TABLE IF EXISTS "travel_bookings" CASCADE;
DROP TABLE IF EXISTS "hotel_room_inventory" CASCADE;
DROP TABLE IF EXISTS "flight_inventory" CASCADE;
DROP TABLE IF EXISTS "hotels" CASCADE;
DROP TABLE IF EXISTS "airlines" CASCADE;
DROP TABLE IF EXISTS "airports" CASCADE;
DROP TABLE IF EXISTS "cities" CASCADE;
DROP TABLE IF EXISTS "travel_requisition_forms" CASCADE;
DROP TABLE IF EXISTS "employee_directory" CASCADE;

DROP TYPE IF EXISTS "traveltype" CASCADE;
DROP TYPE IF EXISTS "trfstatus" CASCADE;
DROP TYPE IF EXISTS "bookingstatus" CASCADE;
DROP TYPE IF EXISTS "cabinclass" CASCADE;
DROP TYPE IF EXISTS "reimbursementstatus" CASCADE;

-- ============================================================================
-- 2. SCHEMA CREATION
-- ============================================================================

CREATE TYPE "traveltype" AS ENUM('DOMESTIC', 'INTERNATIONAL');
CREATE TYPE "trfstatus" AS ENUM('DRAFT', 'PENDING_IRM', 'PENDING_SRM', 'PENDING_BUH', 'PENDING_SSUH', 'PENDING_BGH', 'PENDING_SSGH', 'PENDING_CFO', 'PENDING_TRAVEL_DESK', 'APPROVED', 'REJECTED', 'PROCESSING', 'COMPLETED');
CREATE TYPE "bookingstatus" AS ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED');
CREATE TYPE "cabinclass" AS ENUM('ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST');
CREATE TYPE "reimbursementstatus" AS ENUM('SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'PAID');

CREATE TABLE "airlines" (
	"id" serial PRIMARY KEY,
	"code" varchar(10) NOT NULL,
	"name" varchar(200) NOT NULL,
	"country" varchar(100),
	"is_preferred" boolean,
	"corporate_discount" double precision,
	"created_at" timestamp DEFAULT NOW(),
	"is_active" boolean
);

CREATE TABLE "airports" (
	"id" serial PRIMARY KEY,
	"code" varchar(10) NOT NULL,
	"city" varchar(100) NOT NULL,
	"country" varchar(100) NOT NULL,
	"timezone" varchar(50),
	"created_at" timestamp DEFAULT NOW()
);

CREATE TABLE "cities" (
	"id" serial PRIMARY KEY,
	"city" varchar(100) NOT NULL,
	"country" varchar(100) NOT NULL,
	"currency" varchar(10) NOT NULL,
	"tier_multiplier" double precision,
	"created_at" timestamp DEFAULT NOW()
);

CREATE TABLE "employee_directory" (
	"employee_id" varchar(50) PRIMARY KEY,
	"employee_name" varchar(200) NOT NULL,
	"role" varchar(100),
	"email" varchar(200),
	"department" varchar(100),
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "hotels" (
	"id" serial PRIMARY KEY,
	"name" varchar(200) NOT NULL,
	"chain" varchar(100),
	"rating" integer,
	"city" varchar(100) NOT NULL,
	"country" varchar(100) NOT NULL,
	"address" text,
	"city_tier_multiplier" double precision,
	"corporate_discount" double precision,
	"amenities" json,
	"tags" json,
	"created_at" timestamp DEFAULT NOW(),
	"is_active" boolean
);

CREATE TABLE "hotel_room_inventory" (
	"id" serial PRIMARY KEY,
	"hotel_id" integer NOT NULL,
	"room_type" varchar(100) NOT NULL,
	"occupancy" integer,
	"date" date NOT NULL,
	"base_price" double precision NOT NULL,
	"discounted_price" double precision NOT NULL,
	"is_available" boolean,
	"room_amenities" json,
	"created_at" timestamp DEFAULT NOW()
);

CREATE TABLE "flight_inventory" (
	"id" serial PRIMARY KEY,
	"airline_id" integer NOT NULL,
	"flight_number" varchar(20) NOT NULL,
	"origin_code" varchar(10) NOT NULL,
	"destination_code" varchar(10) NOT NULL,
	"origin_city" varchar(100) NOT NULL,
	"destination_city" varchar(100) NOT NULL,
	"departure_date" date NOT NULL,
	"departure_time" time NOT NULL,
	"arrival_date" date NOT NULL,
	"arrival_time" time NOT NULL,
	"duration_minutes" integer NOT NULL,
	"economy_price" double precision NOT NULL,
	"premium_economy_price" double precision,
	"business_price" double precision,
	"first_price" double precision,
	"is_direct" boolean,
	"layover_city" varchar(100),
	"layover_duration_minutes" integer,
	"is_available" boolean,
	"created_at" timestamp DEFAULT NOW()
);

CREATE TABLE "travel_requisition_forms" (
	"id" serial PRIMARY KEY,
	"trf_number" varchar(50) NOT NULL,
	"employee_id" varchar(50) NOT NULL,
	"employee_name" varchar(200) NOT NULL,
	"employee_email" varchar(200) NOT NULL,
	"employee_phone" varchar(20),
	"employee_department" varchar(100),
	"employee_designation" varchar(100),
	"employee_location" varchar(100),
	"irm_name" varchar(200),
	"irm_email" varchar(200),
	"srm_name" varchar(200),
	"srm_email" varchar(200),
	"travel_type" traveltype NOT NULL,
	"purpose" text NOT NULL,
	"origin_city" varchar(100) NOT NULL,
	"destination_city" varchar(100) NOT NULL,
	"departure_date" date NOT NULL,
	"return_date" date,
	"estimated_cost" double precision,
	"trf_document_path" varchar(500),
	"status" trfstatus NOT NULL,
	"irm_approved_at" timestamp,
	"irm_comments" text,
	"srm_approved_at" timestamp,
	"srm_comments" text,
	"buh_approved_at" timestamp,
	"buh_comments" text,
	"ssuh_approved_at" timestamp,
	"ssuh_comments" text,
	"bgh_approved_at" timestamp,
	"bgh_comments" text,
	"ssgh_approved_at" timestamp,
	"ssgh_comments" text,
	"cfo_approved_at" timestamp,
	"cfo_comments" text,
	"travel_desk_approved_at" timestamp,
	"travel_desk_comments" text,
	"final_approved_at" timestamp,
	"rejection_reason" text,
	"rejected_by" varchar(50),
	"created_at" timestamp DEFAULT NOW(),
	"updated_at" timestamp DEFAULT NOW()
);

CREATE TABLE "travel_bookings" (
	"id" serial PRIMARY KEY,
	"booking_number" varchar(50) NOT NULL,
	"trf_id" integer NOT NULL,
	"traveler_name" varchar(200) NOT NULL,
	"traveler_email" varchar(200) NOT NULL,
	"traveler_phone" varchar(20),
	"traveler_employee_id" varchar(50),
	"travel_desk_agent_name" varchar(200),
	"travel_desk_agent_email" varchar(200),
	"status" bookingstatus NOT NULL,
	"total_flight_cost" double precision,
	"total_hotel_cost" double precision,
	"total_cost" double precision,
	"booking_date" timestamp DEFAULT NOW(),
	"confirmation_date" timestamp,
	"notes" text
);

CREATE TABLE "flight_bookings" (
	"id" serial PRIMARY KEY,
	"pnr" varchar(20) NOT NULL,
	"travel_booking_id" integer NOT NULL,
	"flight_id" integer NOT NULL,
	"cabin_class" cabinclass NOT NULL,
	"passenger_name" varchar(200) NOT NULL,
	"seat_number" varchar(10),
	"base_fare" double precision NOT NULL,
	"taxes" double precision,
	"discount_applied" double precision,
	"final_fare" double precision NOT NULL,
	"status" bookingstatus NOT NULL,
	"booked_at" timestamp DEFAULT NOW()
);

CREATE TABLE "hotel_bookings" (
	"id" serial PRIMARY KEY,
	"confirmation_number" varchar(50) NOT NULL,
	"travel_booking_id" integer NOT NULL,
	"room_id" integer NOT NULL,
	"guest_name" varchar(200) NOT NULL,
	"check_in_date" date NOT NULL,
	"check_out_date" date NOT NULL,
	"number_of_nights" integer NOT NULL,
	"number_of_guests" integer,
	"per_night_rate" double precision NOT NULL,
	"total_room_cost" double precision NOT NULL,
	"discount_applied" double precision,
	"taxes" double precision,
	"final_cost" double precision NOT NULL,
	"status" bookingstatus NOT NULL,
	"special_requests" text,
	"booked_at" timestamp DEFAULT NOW()
);

CREATE TABLE "reimbursements" (
	"id" serial PRIMARY KEY,
	"reimbursement_number" varchar(50) NOT NULL,
	"employee_id" varchar(50) NOT NULL,
	"employee_name" varchar(200) NOT NULL,
	"employee_email" varchar(200) NOT NULL,
	"trf_id" integer,
	"travel_booking_id" integer,
	"category" varchar(100) NOT NULL,
	"amount_claimed" double precision NOT NULL,
	"amount_approved" double precision,
	"description" text NOT NULL,
	"reimbursement_date" date NOT NULL,
	"supporting_documents" json,
	"status" reimbursementstatus NOT NULL,
	"reviewed_by" varchar(200),
	"reviewed_at" timestamp,
	"review_comments" text,
	"payment_date" date,
	"payment_reference" varchar(100),
	"submitted_at" timestamp DEFAULT NOW(),
	"updated_at" timestamp DEFAULT NOW()
);

-- CONSTRAINTS
ALTER TABLE "flight_bookings" ADD CONSTRAINT "flight_bookings_flight_id_fkey" FOREIGN KEY ("flight_id") REFERENCES "flight_inventory"("id");
ALTER TABLE "flight_bookings" ADD CONSTRAINT "flight_bookings_travel_booking_id_fkey" FOREIGN KEY ("travel_booking_id") REFERENCES "travel_bookings"("id");
ALTER TABLE "flight_inventory" ADD CONSTRAINT "flight_inventory_airline_id_fkey" FOREIGN KEY ("airline_id") REFERENCES "airlines"("id");
ALTER TABLE "hotel_bookings" ADD CONSTRAINT "hotel_bookings_room_id_fkey" FOREIGN KEY ("room_id") REFERENCES "hotel_room_inventory"("id");
ALTER TABLE "hotel_bookings" ADD CONSTRAINT "hotel_bookings_travel_booking_id_fkey" FOREIGN KEY ("travel_booking_id") REFERENCES "travel_bookings"("id");
ALTER TABLE "hotel_room_inventory" ADD CONSTRAINT "hotel_room_inventory_hotel_id_fkey" FOREIGN KEY ("hotel_id") REFERENCES "hotels"("id");
ALTER TABLE "reimbursements" ADD CONSTRAINT "reimbursements_travel_booking_id_fkey" FOREIGN KEY ("travel_booking_id") REFERENCES "travel_bookings"("id");
ALTER TABLE "reimbursements" ADD CONSTRAINT "reimbursements_trf_id_fkey" FOREIGN KEY ("trf_id") REFERENCES "travel_requisition_forms"("id");
ALTER TABLE "travel_bookings" ADD CONSTRAINT "travel_bookings_trf_id_fkey" FOREIGN KEY ("trf_id") REFERENCES "travel_requisition_forms"("id");

-- INDEXES (Fixed: Removed redundant _pkey indexes)
CREATE UNIQUE INDEX "ix_airlines_code" ON "airlines" ("code");
CREATE INDEX "ix_airports_city" ON "airports" ("city");
CREATE UNIQUE INDEX "ix_airports_code" ON "airports" ("code");
CREATE UNIQUE INDEX "ix_cities_city" ON "cities" ("city");
CREATE UNIQUE INDEX "ix_flight_bookings_pnr" ON "flight_bookings" ("pnr");
CREATE INDEX "ix_flight_inventory_departure_date" ON "flight_inventory" ("departure_date");
CREATE INDEX "ix_flight_inventory_destination_code" ON "flight_inventory" ("destination_code");
CREATE INDEX "ix_flight_inventory_flight_number" ON "flight_inventory" ("flight_number");
CREATE INDEX "ix_flight_inventory_origin_code" ON "flight_inventory" ("origin_code");
CREATE UNIQUE INDEX "ix_hotel_bookings_confirmation_number" ON "hotel_bookings" ("confirmation_number");
CREATE INDEX "ix_hotel_room_inventory_date" ON "hotel_room_inventory" ("date");
CREATE INDEX "ix_hotels_city" ON "hotels" ("city");
CREATE INDEX "ix_reimbursements_employee_id" ON "reimbursements" ("employee_id");
CREATE UNIQUE INDEX "ix_reimbursements_reimbursement_number" ON "reimbursements" ("reimbursement_number");
CREATE UNIQUE INDEX "ix_travel_bookings_booking_number" ON "travel_bookings" ("booking_number");
CREATE INDEX "ix_travel_requisition_forms_employee_id" ON "travel_requisition_forms" ("employee_id");
CREATE UNIQUE INDEX "ix_travel_requisition_forms_trf_number" ON "travel_requisition_forms" ("trf_number");


-- ============================================================================
-- 3. SEED REFERENCE DATA
-- ============================================================================

INSERT INTO "cities" ("city", "country", "currency", "tier_multiplier") VALUES
('Mumbai', 'India', 'INR', 0.6), ('Delhi', 'India', 'INR', 0.6), ('Bengaluru', 'India', 'INR', 0.6),
('Hyderabad', 'India', 'INR', 0.5), ('Chennai', 'India', 'INR', 0.5), ('Kolkata', 'India', 'INR', 0.5),
('Pune', 'India', 'INR', 0.5), ('Ahmedabad', 'India', 'INR', 0.4), ('Goa', 'India', 'INR', 0.8),
('Kochi', 'India', 'INR', 0.5), ('Jaipur', 'India', 'INR', 0.5),
('Singapore', 'Singapore', 'SGD', 1.8), ('Kuala Lumpur', 'Malaysia', 'MYR', 0.7),
('Bangkok', 'Thailand', 'THB', 0.8), ('Hong Kong', 'China', 'HKD', 1.9), ('Tokyo', 'Japan', 'JPY', 2.0),
('Sydney', 'Australia', 'AUD', 1.8), ('Melbourne', 'Australia', 'AUD', 1.6),
('Dubai', 'United Arab Emirates', 'AED', 1.7), ('Doha', 'Qatar', 'QAR', 1.6), ('Abu Dhabi', 'United Arab Emirates', 'AED', 1.6),
('London', 'United Kingdom', 'GBP', 2.2), ('Paris', 'France', 'EUR', 2.0), ('Frankfurt', 'Germany', 'EUR', 1.6),
('Amsterdam', 'Netherlands', 'EUR', 1.8), ('Zurich', 'Switzerland', 'CHF', 2.5), ('Rome', 'Italy', 'EUR', 1.7),
('New York', 'United States', 'USD', 2.5), ('San Francisco', 'United States', 'USD', 2.4),
('Los Angeles', 'United States', 'USD', 2.2), ('Chicago', 'United States', 'USD', 1.9), ('Toronto', 'Canada', 'CAD', 1.8);

INSERT INTO "airports" ("code", "city", "country", "timezone") VALUES
('BOM', 'Mumbai', 'India', 'Asia/Kolkata'), ('DEL', 'Delhi', 'India', 'Asia/Kolkata'),
('BLR', 'Bengaluru', 'India', 'Asia/Kolkata'), ('HYD', 'Hyderabad', 'India', 'Asia/Kolkata'),
('MAA', 'Chennai', 'India', 'Asia/Kolkata'), ('CCU', 'Kolkata', 'India', 'Asia/Kolkata'),
('PNQ', 'Pune', 'India', 'Asia/Kolkata'), ('AMD', 'Ahmedabad', 'India', 'Asia/Kolkata'),
('GOI', 'Goa', 'India', 'Asia/Kolkata'), ('COK', 'Kochi', 'India', 'Asia/Kolkata'),
('JAI', 'Jaipur', 'India', 'Asia/Kolkata'),
('SIN', 'Singapore', 'Singapore', 'Asia/Singapore'), ('KUL', 'Kuala Lumpur', 'Malaysia', 'Asia/Kuala_Lumpur'),
('BKK', 'Bangkok', 'Thailand', 'Asia/Bangkok'), ('HKG', 'Hong Kong', 'China', 'Asia/Hong_Kong'),
('HND', 'Tokyo', 'Japan', 'Asia/Tokyo'),
('SYD', 'Sydney', 'Australia', 'Australia/Sydney'), ('MEL', 'Melbourne', 'Australia', 'Australia/Melbourne'),
('DXB', 'Dubai', 'United Arab Emirates', 'Asia/Dubai'), ('DOH', 'Doha', 'Qatar', 'Asia/Qatar'),
('AUH', 'Abu Dhabi', 'United Arab Emirates', 'Asia/Dubai'),
('LHR', 'London', 'United Kingdom', 'Europe/London'), ('CDG', 'Paris', 'France', 'Europe/Paris'),
('FRA', 'Frankfurt', 'Germany', 'Europe/Berlin'), ('AMS', 'Amsterdam', 'Netherlands', 'Europe/Amsterdam'),
('ZRH', 'Zurich', 'Switzerland', 'Europe/Zurich'), ('FCO', 'Rome', 'Italy', 'Europe/Rome'),
('JFK', 'New York', 'United States', 'America/New_York'), ('SFO', 'San Francisco', 'United States', 'America/Los_Angeles'),
('LAX', 'Los Angeles', 'United States', 'America/Los_Angeles'), ('ORD', 'Chicago', 'United States', 'America/Chicago'),
('YYZ', 'Toronto', 'Canada', 'America/Toronto');

INSERT INTO "airlines" ("code", "name", "country", "is_preferred", "corporate_discount", "is_active") VALUES
('YA', 'Yash Air', 'India', true, 18.0, true),
('AI', 'Air India Corporate', 'India', true, 12.0, true),
('SG', 'Singapore Global', 'Singapore', true, 14.0, true),
('EK', 'Emirates Connect', 'United Arab Emirates', false, 10.0, true),
('QR', 'Qatar Connect', 'Qatar', true, 11.0, true),
('BA', 'Britannia Airways', 'United Kingdom', false, 8.0, true),
('LH', 'Deutsche Hansa', 'Germany', false, 8.0, true),
('AF', 'Air Francais', 'France', false, 7.0, true),
('UA', 'United Atlantic', 'United States', false, 6.0, true),
('DL', 'Delta Skies', 'United States', true, 9.0, true),
('JL', 'Japan Global', 'Japan', false, 5.0, true),
('CX', 'Cathay Pacific', 'China', false, 6.0, true);


-- ============================================================================
-- 4. SEED HOTELS (Dynamic mix of Chains + Cities)
-- ============================================================================

INSERT INTO "hotels" ("name", "chain", "rating", "city", "country", "address", "city_tier_multiplier", "corporate_discount", "amenities", "tags", "is_active")
WITH hotel_chains (name, rating, discount, tags) AS (
    VALUES 
    ('Grand Hyatt', 5, 15.0, '["Luxury", "Business"]'::json),
    ('Marriott Marquis', 5, 18.0, '["Luxury", "Business"]'::json),
    ('Hilton Garden', 4, 12.0, '["Business", "Comfort"]'::json),
    ('Sheraton', 4, 12.0, '["Business"]'::json),
    ('Holiday Inn', 3, 10.0, '["Budget", "Family"]'::json),
    ('Novotel', 4, 10.0, '["Business", "Modern"]'::json),
    ('Four Seasons', 5, 8.0, '["Ultra-Luxury"]'::json),
    ('Ibis Styles', 3, 5.0, '["Budget", "Modern"]'::json),
    ('Radisson Blu', 4, 14.0, '["Business", "Airport"]'::json),
    ('Taj Palace', 5, 15.0, '["Heritage", "Luxury"]'::json)
),
suffixes (txt) AS ( VALUES ('Plaza'), ('Residency'), ('Suites'), ('Towers'), ('Inn') ),
city_list AS (SELECT * FROM "cities"),
hotel_counts AS (SELECT generate_series(1, 4) as n) -- 4 hotels per city

SELECT 
    hc.name || ' ' || cl.city || ' ' || s.txt, -- Name
    hc.name, -- Chain
    hc.rating,
    cl.city,
    cl.country,
    (floor(random() * 900 + 10)::text || ' Business District, ' || cl.city), -- Address
    cl.tier_multiplier,
    hc.discount,
    '["Free WiFi", "Gym", "Breakfast"]'::json, -- Standard Amenities
    hc.tags,
    true -- is_active
FROM city_list cl
CROSS JOIN hotel_counts hnum
CROSS JOIN LATERAL (SELECT * FROM hotel_chains ORDER BY random() LIMIT 1) hc
CROSS JOIN LATERAL (SELECT * FROM suffixes ORDER BY random() LIMIT 1) s;


-- ============================================================================
-- 5. SEED HOTEL ROOM INVENTORY (180 Days)
-- ============================================================================

INSERT INTO "hotel_room_inventory" (
    "hotel_id", "room_type", "occupancy", "date", "base_price", "discounted_price", "is_available", "room_amenities"
)
WITH 
room_types (rtype, mult, occ) AS (
    VALUES 
    ('Standard King', 1.0, 2),
    ('Twin Deluxe', 1.2, 2),
    ('Club Room', 1.6, 2),
    ('Executive Suite', 2.5, 3),
    ('Presidential Suite', 5.0, 4)
),
base_prices (rating, price) AS ( VALUES (3, 3000), (4, 6000), (5, 12000) ),
dates AS (SELECT generate_series(CURRENT_DATE, CURRENT_DATE + INTERVAL '180 days', '1 day')::date as h_date)

SELECT 
    h.id,
    rt.rtype,
    rt.occ,
    d.h_date,
    -- Price Calc: Base(Rating) * CityMultiplier * RoomTypeMultiplier
    (bp.price * h.city_tier_multiplier * rt.mult)::float as raw_price,
    -- Discount Calc: Raw - (Raw * CorpDiscount%)
    ((bp.price * h.city_tier_multiplier * rt.mult) * (1 - (h.corporate_discount/100)))::float,
    TRUE,
    '["TV", "AC", "Safe"]'::json
FROM "hotels" h
JOIN base_prices bp ON bp.rating = h.rating
CROSS JOIN room_types rt
CROSS JOIN dates d;


-- ============================================================================
-- 6. SEED FLIGHT INVENTORY (180 Days, Full Expanded Routes)
-- ============================================================================

INSERT INTO "flight_inventory" (
	"airline_id", "flight_number", "origin_code", "destination_code", "origin_city", "destination_city",
	"departure_date", "departure_time", "arrival_date", "arrival_time", "duration_minutes",
	"economy_price", "premium_economy_price", "business_price", "first_price",
	"is_direct", "is_available"
)
WITH 
-- Define Routes, Prices, Duration and Frequency per Airline
route_data (org, dst, al, price, dur, freq) AS (
    VALUES 
    -- DOMESTIC INDIA
    ('BOM', 'DEL', 'YA', 5800, 140, 8), ('BOM', 'DEL', 'AI', 5800, 140, 8),
    ('DEL', 'BLR', 'YA', 6200, 150, 6), ('DEL', 'BLR', 'AI', 6200, 150, 6),
    ('BLR', 'HYD', 'YA', 4500, 80, 5),
    ('MAA', 'BOM', 'YA', 5600, 115, 4), ('MAA', 'BOM', 'AI', 5600, 115, 4),
    ('CCU', 'BOM', 'YA', 6100, 165, 4), ('CCU', 'BOM', 'AI', 6100, 165, 4),
    ('PNQ', 'DEL', 'YA', 5200, 125, 3),
    ('AMD', 'BOM', 'YA', 4800, 110, 3),
    ('GOI', 'BLR', 'YA', 4200, 70, 3),
    ('COK', 'DEL', 'YA', 7500, 190, 2),
    ('JAI', 'BOM', 'YA', 4900, 105, 2),
    -- ASIA/PACIFIC
    ('BOM', 'SIN', 'YA', 32000, 330, 4), ('BOM', 'SIN', 'SG', 32000, 330, 4), ('BOM', 'SIN', 'EK', 32000, 330, 4),
    ('DEL', 'BKK', 'YA', 24000, 240, 3), ('DEL', 'BKK', 'AI', 24000, 240, 3),
    ('BLR', 'SIN', 'YA', 29500, 320, 2), ('BLR', 'SIN', 'SG', 29500, 320, 2),
    ('DEL', 'HND', 'JL', 55000, 450, 2), ('DEL', 'HND', 'AI', 55000, 450, 2),
    ('DEL', 'HKG', 'CX', 38000, 300, 2), ('DEL', 'HKG', 'AI', 38000, 300, 2),
    ('SIN', 'SYD', 'SG', 65000, 480, 3),
    ('HND', 'SYD', 'JL', 78000, 570, 2),
    -- MIDDLE EAST
    ('DEL', 'DXB', 'YA', 26000, 240, 5), ('DEL', 'DXB', 'EK', 26000, 240, 5), ('DEL', 'DXB', 'AI', 26000, 240, 5),
    ('BOM', 'DXB', 'YA', 24000, 210, 5), ('BOM', 'DXB', 'EK', 24000, 210, 5),
    ('DEL', 'DOH', 'QR', 28000, 230, 4), ('DEL', 'DOH', 'AI', 28000, 230, 4),
    ('HYD', 'AUH', 'EK', 22000, 220, 2),
    -- EUROPE
    ('DEL', 'LHR', 'BA', 65000, 580, 4), ('DEL', 'LHR', 'AI', 65000, 580, 4), ('DEL', 'LHR', 'YA', 65000, 580, 4),
    ('BOM', 'LHR', 'BA', 62000, 590, 3), ('BOM', 'LHR', 'AI', 62000, 590, 3),
    ('DEL', 'FRA', 'LH', 54000, 520, 3), ('DEL', 'FRA', 'AI', 54000, 520, 3),
    ('BLR', 'FRA', 'LH', 56000, 540, 2),
    ('DEL', 'CDG', 'AF', 58000, 560, 2), ('DEL', 'CDG', 'AI', 58000, 560, 2),
    ('BOM', 'AMS', 'YA', 59000, 570, 2),
    ('DEL', 'ZRH', 'AI', 61000, 530, 2),
    -- AMERICAS
    ('BOM', 'JFK', 'UA', 89000, 960, 2), ('BOM', 'JFK', 'AI', 89000, 960, 2),
    ('DEL', 'JFK', 'AI', 85000, 920, 2), ('DEL', 'JFK', 'UA', 85000, 920, 2),
    ('DEL', 'SFO', 'AI', 95000, 990, 2), ('DEL', 'SFO', 'UA', 95000, 990, 2),
    ('BLR', 'SFO', 'AI', 105000, 1050, 1),
    ('DXB', 'JFK', 'EK', 110000, 850, 3),
    ('DOH', 'LAX', 'QR', 115000, 980, 2),
    ('LHR', 'JFK', 'BA', 75000, 480, 6), ('LHR', 'JFK', 'UA', 75000, 480, 6), ('LHR', 'JFK', 'DL', 75000, 480, 6),
    ('CDG', 'JFK', 'AF', 72000, 500, 4), ('CDG', 'JFK', 'DL', 72000, 500, 4),
    ('HND', 'LAX', 'JL', 82000, 600, 4), ('HND', 'LAX', 'UA', 82000, 600, 4)
),
-- Generate 180 Days
dates AS (SELECT generate_series(CURRENT_DATE, CURRENT_DATE + INTERVAL '180 days', '1 day')::date as f_date),
-- Explode frequencies (e.g. freq 8 = 8 rows)
freqs AS (SELECT generate_series(1, 8) as fn)

SELECT 
    al."id",
    al."code" || (floor(random()*899+100)::text),
    rd.org, rd.dst,
    orig."city", dest."city",
    d.f_date,
    (d.f_date + make_time((5 + (f.fn * (18/rd.freq))::int % 24), (random()*59)::int, 0))::time,
    (d.f_date + make_time((5 + (f.fn * (18/rd.freq))::int % 24), (random()*59)::int, 0) + (rd.dur || ' mins')::interval)::date,
    (d.f_date + make_time((5 + (f.fn * (18/rd.freq))::int % 24), (random()*59)::int, 0) + (rd.dur || ' mins')::interval)::time,
    rd.dur,
    (rd.price * (0.8 + random()*0.4))::float,
    CASE WHEN random() > 0.5 THEN (rd.price * 1.5)::float ELSE NULL END,
    CASE WHEN random() > 0.3 THEN (rd.price * 3.5)::float ELSE NULL END,
    CASE WHEN random() > 0.8 THEN (rd.price * 6.0)::float ELSE NULL END,
    TRUE, TRUE
FROM route_data rd
CROSS JOIN dates d
JOIN freqs f ON f.fn <= rd.freq
JOIN "airlines" al ON al."code" = rd.al
JOIN "airports" orig ON orig."code" = rd.org
JOIN "airports" dest ON dest."code" = rd.dst;

COMMIT;

-- ============================================================================
-- 7. VERIFICATION
-- ============================================================================
SELECT 
    (SELECT count(*) FROM "cities") as cities_count,
    (SELECT count(*) FROM "hotels") as hotels_count,
    (SELECT count(*) FROM "flight_inventory") as flights_generated,
    (SELECT count(*) FROM "hotel_room_inventory") as hotel_rooms_generated;