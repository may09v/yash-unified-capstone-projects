 CREATE SCHEMA "public";
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
	"created_at" timestamp,
	"is_active" boolean
);
CREATE TABLE "airports" (
	"id" serial PRIMARY KEY,
	"code" varchar(10) NOT NULL,
	"city" varchar(100) NOT NULL,
	"country" varchar(100) NOT NULL,
	"timezone" varchar(50),
	"created_at" timestamp
);
CREATE TABLE "cities" (
	"id" serial PRIMARY KEY,
	"city" varchar(100) NOT NULL,
	"country" varchar(100) NOT NULL,
	"currency" varchar(10) NOT NULL,
	"tier_multiplier" double precision,
	"created_at" timestamp
);
CREATE TABLE "employee_directory" (
	"employee_id" varchar(50) PRIMARY KEY,
	"employee_name" varchar(200) NOT NULL,
	"role" varchar(100),
	"email" varchar(200),
	"department" varchar(100),
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
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
	"booked_at" timestamp
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
	"created_at" timestamp
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
	"booked_at" timestamp
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
	"created_at" timestamp
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
	"created_at" timestamp,
	"is_active" boolean
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
	"submitted_at" timestamp,
	"updated_at" timestamp
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
	"booking_date" timestamp,
	"confirmation_date" timestamp,
	"notes" text
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
	"created_at" timestamp,
	"updated_at" timestamp
);
ALTER TABLE "flight_bookings" ADD CONSTRAINT "flight_bookings_flight_id_fkey" FOREIGN KEY ("flight_id") REFERENCES "flight_inventory"("id");
ALTER TABLE "flight_bookings" ADD CONSTRAINT "flight_bookings_travel_booking_id_fkey" FOREIGN KEY ("travel_booking_id") REFERENCES "travel_bookings"("id");
ALTER TABLE "flight_inventory" ADD CONSTRAINT "flight_inventory_airline_id_fkey" FOREIGN KEY ("airline_id") REFERENCES "airlines"("id");
ALTER TABLE "hotel_bookings" ADD CONSTRAINT "hotel_bookings_room_id_fkey" FOREIGN KEY ("room_id") REFERENCES "hotel_room_inventory"("id");
ALTER TABLE "hotel_bookings" ADD CONSTRAINT "hotel_bookings_travel_booking_id_fkey" FOREIGN KEY ("travel_booking_id") REFERENCES "travel_bookings"("id");
ALTER TABLE "hotel_room_inventory" ADD CONSTRAINT "hotel_room_inventory_hotel_id_fkey" FOREIGN KEY ("hotel_id") REFERENCES "hotels"("id");
ALTER TABLE "reimbursements" ADD CONSTRAINT "reimbursements_travel_booking_id_fkey" FOREIGN KEY ("travel_booking_id") REFERENCES "travel_bookings"("id");
ALTER TABLE "reimbursements" ADD CONSTRAINT "reimbursements_trf_id_fkey" FOREIGN KEY ("trf_id") REFERENCES "travel_requisition_forms"("id");
ALTER TABLE "travel_bookings" ADD CONSTRAINT "travel_bookings_trf_id_fkey" FOREIGN KEY ("trf_id") REFERENCES "travel_requisition_forms"("id");
CREATE UNIQUE INDEX "airlines_pkey" ON "airlines" ("id");
CREATE UNIQUE INDEX "ix_airlines_code" ON "airlines" ("code");
CREATE UNIQUE INDEX "airports_pkey" ON "airports" ("id");
CREATE INDEX "ix_airports_city" ON "airports" ("city");
CREATE UNIQUE INDEX "ix_airports_code" ON "airports" ("code");
CREATE UNIQUE INDEX "cities_pkey" ON "cities" ("id");
CREATE UNIQUE INDEX "ix_cities_city" ON "cities" ("city");
CREATE UNIQUE INDEX "employee_directory_pkey" ON "employee_directory" ("employee_id");
CREATE UNIQUE INDEX "flight_bookings_pkey" ON "flight_bookings" ("id");
CREATE UNIQUE INDEX "ix_flight_bookings_pnr" ON "flight_bookings" ("pnr");
CREATE UNIQUE INDEX "flight_inventory_pkey" ON "flight_inventory" ("id");
CREATE INDEX "ix_flight_inventory_departure_date" ON "flight_inventory" ("departure_date");
CREATE INDEX "ix_flight_inventory_destination_code" ON "flight_inventory" ("destination_code");
CREATE INDEX "ix_flight_inventory_flight_number" ON "flight_inventory" ("flight_number");
CREATE INDEX "ix_flight_inventory_origin_code" ON "flight_inventory" ("origin_code");
CREATE UNIQUE INDEX "hotel_bookings_pkey" ON "hotel_bookings" ("id");
CREATE UNIQUE INDEX "ix_hotel_bookings_confirmation_number" ON "hotel_bookings" ("confirmation_number");
CREATE UNIQUE INDEX "hotel_room_inventory_pkey" ON "hotel_room_inventory" ("id");
CREATE INDEX "ix_hotel_room_inventory_date" ON "hotel_room_inventory" ("date");
CREATE UNIQUE INDEX "hotels_pkey" ON "hotels" ("id");
CREATE INDEX "ix_hotels_city" ON "hotels" ("city");
CREATE INDEX "ix_reimbursements_employee_id" ON "reimbursements" ("employee_id");
CREATE UNIQUE INDEX "ix_reimbursements_reimbursement_number" ON "reimbursements" ("reimbursement_number");
CREATE UNIQUE INDEX "reimbursements_pkey" ON "reimbursements" ("id");
CREATE UNIQUE INDEX "ix_travel_bookings_booking_number" ON "travel_bookings" ("booking_number");
CREATE UNIQUE INDEX "travel_bookings_pkey" ON "travel_bookings" ("id");
CREATE INDEX "ix_travel_requisition_forms_employee_id" ON "travel_requisition_forms" ("employee_id");
CREATE UNIQUE INDEX "ix_travel_requisition_forms_trf_number" ON "travel_requisition_forms" ("trf_number");
CREATE UNIQUE INDEX "travel_requisition_forms_pkey" ON "travel_requisition_forms" ("id");
