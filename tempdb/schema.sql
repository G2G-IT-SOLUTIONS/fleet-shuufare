--
-- PostgreSQL database dump
--

\restrict WP2GVyIsC5aeSGzWsahkgjwVhc7zTcmusSSlnFNrGrAqP40oUTokNJR8J9ssLYk

-- Dumped from database version 15.18
-- Dumped by pg_dump version 15.18

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auditlog; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.auditlog (
    id integer NOT NULL,
    target_type character varying NOT NULL,
    target_id character varying NOT NULL,
    field_name character varying NOT NULL,
    old_value character varying,
    new_value character varying,
    user_id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.auditlog OWNER TO postgres_admin;

--
-- Name: auditlog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.auditlog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auditlog_id_seq OWNER TO postgres_admin;

--
-- Name: auditlog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.auditlog_id_seq OWNED BY public.auditlog.id;


--
-- Name: deposittriplink; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.deposittriplink (
    id integer NOT NULL,
    transaction_id character varying NOT NULL,
    trip_id character varying NOT NULL,
    amount_applied double precision NOT NULL,
    batch_id integer,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.deposittriplink OWNER TO postgres_admin;

--
-- Name: deposittriplink_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.deposittriplink_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deposittriplink_id_seq OWNER TO postgres_admin;

--
-- Name: deposittriplink_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.deposittriplink_id_seq OWNED BY public.deposittriplink.id;


--
-- Name: driver; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.driver (
    id integer NOT NULL,
    yango_driver_id character varying NOT NULL,
    name character varying NOT NULL,
    phone character varying,
    operator_id character varying NOT NULL,
    driver_type character varying NOT NULL,
    shift character varying NOT NULL,
    reconciliation_start_date date,
    avatar_data character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.driver OWNER TO postgres_admin;

--
-- Name: driver_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.driver_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_id_seq OWNER TO postgres_admin;

--
-- Name: driver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.driver_id_seq OWNED BY public.driver.id;


--
-- Name: driverdocument; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.driverdocument (
    id integer NOT NULL,
    driver_id integer NOT NULL,
    document_type character varying NOT NULL,
    filename character varying NOT NULL,
    content_type character varying NOT NULL,
    file_data character varying NOT NULL,
    uploaded_at timestamp without time zone NOT NULL,
    notes character varying
);


ALTER TABLE public.driverdocument OWNER TO postgres_admin;

--
-- Name: driverdocument_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.driverdocument_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driverdocument_id_seq OWNER TO postgres_admin;

--
-- Name: driverdocument_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.driverdocument_id_seq OWNED BY public.driverdocument.id;


--
-- Name: drivertrip; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.drivertrip (
    id character varying NOT NULL,
    short_id integer,
    driver_id integer NOT NULL,
    status character varying NOT NULL,
    category character varying,
    payment_method character varying,
    price double precision,
    provider character varying,
    booked_at timestamp without time zone,
    yango_created_at timestamp without time zone,
    ended_at timestamp without time zone,
    address_from character varying,
    address_from_lat double precision,
    address_from_lon double precision,
    car_id character varying,
    car_brand_model character varying,
    car_license character varying,
    car_callsign character varying,
    order_type_name character varying,
    driver_work_rule character varying,
    passenger_name character varying,
    mileage character varying,
    deposited_amount double precision NOT NULL,
    reconciliation_status character varying NOT NULL,
    reconciliation_notes character varying,
    synced_at timestamp without time zone NOT NULL
);


ALTER TABLE public.drivertrip OWNER TO postgres_admin;

--
-- Name: expectedrevenue; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.expectedrevenue (
    id integer NOT NULL,
    driver_id integer NOT NULL,
    date date NOT NULL,
    expected_amount double precision NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.expectedrevenue OWNER TO postgres_admin;

--
-- Name: expectedrevenue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.expectedrevenue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expectedrevenue_id_seq OWNER TO postgres_admin;

--
-- Name: expectedrevenue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.expectedrevenue_id_seq OWNED BY public.expectedrevenue.id;


--
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.notification (
    id integer NOT NULL,
    title character varying NOT NULL,
    message character varying NOT NULL,
    type character varying NOT NULL,
    is_read boolean NOT NULL,
    action_url character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.notification OWNER TO postgres_admin;

--
-- Name: notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notification_id_seq OWNER TO postgres_admin;

--
-- Name: notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.notification_id_seq OWNED BY public.notification.id;


--
-- Name: order; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public."order" (
    id character varying NOT NULL,
    short_id integer NOT NULL,
    status character varying NOT NULL,
    price double precision NOT NULL,
    payment_method character varying NOT NULL,
    driver_id character varying NOT NULL,
    driver_name character varying NOT NULL,
    ended_at timestamp without time zone NOT NULL,
    address_from character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public."order" OWNER TO postgres_admin;

--
-- Name: reconciliationbatch; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.reconciliationbatch (
    id integer NOT NULL,
    filename character varying NOT NULL,
    uploaded_by integer NOT NULL,
    total_transactions integer NOT NULL,
    total_amount double precision NOT NULL,
    drivers_matched integer NOT NULL,
    trips_reconciled integer NOT NULL,
    status character varying NOT NULL,
    created_at timestamp without time zone NOT NULL,
    reversed_at timestamp without time zone,
    reversed_by integer
);


ALTER TABLE public.reconciliationbatch OWNER TO postgres_admin;

--
-- Name: reconciliationbatch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.reconciliationbatch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reconciliationbatch_id_seq OWNER TO postgres_admin;

--
-- Name: reconciliationbatch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.reconciliationbatch_id_seq OWNED BY public.reconciliationbatch.id;


--
-- Name: reconciliationrecord; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.reconciliationrecord (
    id integer NOT NULL,
    driver_id integer NOT NULL,
    date date NOT NULL,
    expected_amount double precision NOT NULL,
    actual_amount double precision NOT NULL,
    status character varying NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.reconciliationrecord OWNER TO postgres_admin;

--
-- Name: reconciliationrecord_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.reconciliationrecord_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reconciliationrecord_id_seq OWNER TO postgres_admin;

--
-- Name: reconciliationrecord_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.reconciliationrecord_id_seq OWNED BY public.reconciliationrecord.id;


--
-- Name: systemconfig; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.systemconfig (
    key character varying NOT NULL,
    value character varying NOT NULL,
    description character varying NOT NULL,
    data_type character varying NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.systemconfig OWNER TO postgres_admin;

--
-- Name: telebirrtransaction; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public.telebirrtransaction (
    id integer NOT NULL,
    transaction_id character varying NOT NULL,
    amount double precision NOT NULL,
    sender_identifier character varying NOT NULL,
    merchant_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    status character varying NOT NULL,
    opposite_party character varying,
    is_reconciled boolean NOT NULL,
    driver_id integer,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.telebirrtransaction OWNER TO postgres_admin;

--
-- Name: telebirrtransaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.telebirrtransaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telebirrtransaction_id_seq OWNER TO postgres_admin;

--
-- Name: telebirrtransaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.telebirrtransaction_id_seq OWNED BY public.telebirrtransaction.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres_admin
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    full_name character varying,
    phone character varying,
    two_factor_enabled boolean NOT NULL,
    role character varying NOT NULL,
    is_active boolean NOT NULL,
    last_login timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public."user" OWNER TO postgres_admin;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres_admin
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO postgres_admin;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres_admin
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: auditlog id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.auditlog ALTER COLUMN id SET DEFAULT nextval('public.auditlog_id_seq'::regclass);


--
-- Name: deposittriplink id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.deposittriplink ALTER COLUMN id SET DEFAULT nextval('public.deposittriplink_id_seq'::regclass);


--
-- Name: driver id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.driver ALTER COLUMN id SET DEFAULT nextval('public.driver_id_seq'::regclass);


--
-- Name: driverdocument id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.driverdocument ALTER COLUMN id SET DEFAULT nextval('public.driverdocument_id_seq'::regclass);


--
-- Name: expectedrevenue id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.expectedrevenue ALTER COLUMN id SET DEFAULT nextval('public.expectedrevenue_id_seq'::regclass);


--
-- Name: notification id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.notification ALTER COLUMN id SET DEFAULT nextval('public.notification_id_seq'::regclass);


--
-- Name: reconciliationbatch id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.reconciliationbatch ALTER COLUMN id SET DEFAULT nextval('public.reconciliationbatch_id_seq'::regclass);


--
-- Name: reconciliationrecord id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.reconciliationrecord ALTER COLUMN id SET DEFAULT nextval('public.reconciliationrecord_id_seq'::regclass);


--
-- Name: telebirrtransaction id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.telebirrtransaction ALTER COLUMN id SET DEFAULT nextval('public.telebirrtransaction_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: auditlog auditlog_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.auditlog
    ADD CONSTRAINT auditlog_pkey PRIMARY KEY (id);


--
-- Name: deposittriplink deposittriplink_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_pkey PRIMARY KEY (id);


--
-- Name: driver driver_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.driver
    ADD CONSTRAINT driver_pkey PRIMARY KEY (id);


--
-- Name: driverdocument driverdocument_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.driverdocument
    ADD CONSTRAINT driverdocument_pkey PRIMARY KEY (id);


--
-- Name: drivertrip drivertrip_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.drivertrip
    ADD CONSTRAINT drivertrip_pkey PRIMARY KEY (id);


--
-- Name: expectedrevenue expectedrevenue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.expectedrevenue
    ADD CONSTRAINT expectedrevenue_pkey PRIMARY KEY (id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- Name: reconciliationbatch reconciliationbatch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.reconciliationbatch
    ADD CONSTRAINT reconciliationbatch_pkey PRIMARY KEY (id);


--
-- Name: reconciliationrecord reconciliationrecord_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.reconciliationrecord
    ADD CONSTRAINT reconciliationrecord_pkey PRIMARY KEY (id);


--
-- Name: systemconfig systemconfig_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.systemconfig
    ADD CONSTRAINT systemconfig_pkey PRIMARY KEY (key);


--
-- Name: telebirrtransaction telebirrtransaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.telebirrtransaction
    ADD CONSTRAINT telebirrtransaction_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: ix_auditlog_target_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_auditlog_target_id ON public.auditlog USING btree (target_id);


--
-- Name: ix_auditlog_target_type; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_auditlog_target_type ON public.auditlog USING btree (target_type);


--
-- Name: ix_deposittriplink_batch_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_deposittriplink_batch_id ON public.deposittriplink USING btree (batch_id);


--
-- Name: ix_deposittriplink_transaction_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_deposittriplink_transaction_id ON public.deposittriplink USING btree (transaction_id);


--
-- Name: ix_deposittriplink_trip_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_deposittriplink_trip_id ON public.deposittriplink USING btree (trip_id);


--
-- Name: ix_driver_driver_type; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_driver_driver_type ON public.driver USING btree (driver_type);


--
-- Name: ix_driver_operator_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_driver_operator_id ON public.driver USING btree (operator_id);


--
-- Name: ix_driver_shift; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_driver_shift ON public.driver USING btree (shift);


--
-- Name: ix_driver_yango_driver_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE UNIQUE INDEX ix_driver_yango_driver_id ON public.driver USING btree (yango_driver_id);


--
-- Name: ix_driverdocument_document_type; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_driverdocument_document_type ON public.driverdocument USING btree (document_type);


--
-- Name: ix_order_driver_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_order_driver_id ON public."order" USING btree (driver_id);


--
-- Name: ix_order_ended_at; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_order_ended_at ON public."order" USING btree (ended_at);


--
-- Name: ix_telebirrtransaction_sender_identifier; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_telebirrtransaction_sender_identifier ON public.telebirrtransaction USING btree (sender_identifier);


--
-- Name: ix_telebirrtransaction_transaction_id; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE UNIQUE INDEX ix_telebirrtransaction_transaction_id ON public.telebirrtransaction USING btree (transaction_id);


--
-- Name: ix_user_email; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE UNIQUE INDEX ix_user_email ON public."user" USING btree (email);


--
-- Name: ix_user_phone; Type: INDEX; Schema: public; Owner: postgres_admin
--

CREATE INDEX ix_user_phone ON public."user" USING btree (phone);


--
-- Name: auditlog auditlog_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.auditlog
    ADD CONSTRAINT auditlog_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: deposittriplink deposittriplink_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.reconciliationbatch(id);


--
-- Name: deposittriplink deposittriplink_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.telebirrtransaction(transaction_id);


--
-- Name: deposittriplink deposittriplink_trip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.drivertrip(id);


--
-- Name: driverdocument driverdocument_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.driverdocument
    ADD CONSTRAINT driverdocument_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: drivertrip drivertrip_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.drivertrip
    ADD CONSTRAINT drivertrip_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: expectedrevenue expectedrevenue_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.expectedrevenue
    ADD CONSTRAINT expectedrevenue_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: reconciliationbatch reconciliationbatch_reversed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.reconciliationbatch
    ADD CONSTRAINT reconciliationbatch_reversed_by_fkey FOREIGN KEY (reversed_by) REFERENCES public."user"(id);


--
-- Name: reconciliationbatch reconciliationbatch_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.reconciliationbatch
    ADD CONSTRAINT reconciliationbatch_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public."user"(id);


--
-- Name: reconciliationrecord reconciliationrecord_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.reconciliationrecord
    ADD CONSTRAINT reconciliationrecord_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: telebirrtransaction telebirrtransaction_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres_admin
--

ALTER TABLE ONLY public.telebirrtransaction
    ADD CONSTRAINT telebirrtransaction_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- PostgreSQL database dump complete
--

\unrestrict WP2GVyIsC5aeSGzWsahkgjwVhc7zTcmusSSlnFNrGrAqP40oUTokNJR8J9ssLYk

