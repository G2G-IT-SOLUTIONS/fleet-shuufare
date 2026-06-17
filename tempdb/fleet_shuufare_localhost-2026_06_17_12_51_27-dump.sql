--
-- PostgreSQL database dump
--

\restrict HM07kUkqD3LgLN17mCacpmQaASTZXdqup2o1jPrUhaOOxLfc3bNOv4oOwr5n2bH

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: auditlog; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.auditlog OWNER TO postgres;

--
-- Name: auditlog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auditlog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.auditlog_id_seq OWNER TO postgres;

--
-- Name: auditlog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auditlog_id_seq OWNED BY public.auditlog.id;


--
-- Name: deposittriplink; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deposittriplink (
    id integer NOT NULL,
    transaction_id character varying NOT NULL,
    trip_id character varying NOT NULL,
    amount_applied double precision NOT NULL,
    batch_id integer,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.deposittriplink OWNER TO postgres;

--
-- Name: deposittriplink_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deposittriplink_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.deposittriplink_id_seq OWNER TO postgres;

--
-- Name: deposittriplink_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deposittriplink_id_seq OWNED BY public.deposittriplink.id;


--
-- Name: driver; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.driver OWNER TO postgres;

--
-- Name: driver_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_id_seq OWNER TO postgres;

--
-- Name: driver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_id_seq OWNED BY public.driver.id;


--
-- Name: driverdocument; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.driverdocument OWNER TO postgres;

--
-- Name: driverdocument_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driverdocument_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driverdocument_id_seq OWNER TO postgres;

--
-- Name: driverdocument_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driverdocument_id_seq OWNED BY public.driverdocument.id;


--
-- Name: drivertrip; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.drivertrip OWNER TO postgres;

--
-- Name: expectedrevenue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expectedrevenue (
    id integer NOT NULL,
    driver_id integer NOT NULL,
    date date NOT NULL,
    expected_amount double precision NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.expectedrevenue OWNER TO postgres;

--
-- Name: expectedrevenue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expectedrevenue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expectedrevenue_id_seq OWNER TO postgres;

--
-- Name: expectedrevenue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expectedrevenue_id_seq OWNED BY public.expectedrevenue.id;


--
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.notification OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_id_seq OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_id_seq OWNED BY public.notification.id;


--
-- Name: order; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public."order" OWNER TO postgres;

--
-- Name: profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profiles (
    id integer NOT NULL,
    name character varying(55) NOT NULL,
    email character varying(55),
    age integer
);


ALTER TABLE public.profiles OWNER TO postgres;

--
-- Name: profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profiles_id_seq OWNER TO postgres;

--
-- Name: profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.profiles_id_seq OWNED BY public.profiles.id;


--
-- Name: reconciliationbatch; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.reconciliationbatch OWNER TO postgres;

--
-- Name: reconciliationbatch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reconciliationbatch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reconciliationbatch_id_seq OWNER TO postgres;

--
-- Name: reconciliationbatch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reconciliationbatch_id_seq OWNED BY public.reconciliationbatch.id;


--
-- Name: reconciliationrecord; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.reconciliationrecord OWNER TO postgres;

--
-- Name: reconciliationrecord_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reconciliationrecord_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reconciliationrecord_id_seq OWNER TO postgres;

--
-- Name: reconciliationrecord_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reconciliationrecord_id_seq OWNED BY public.reconciliationrecord.id;


--
-- Name: systemconfig; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.systemconfig (
    key character varying NOT NULL,
    value character varying NOT NULL,
    description character varying NOT NULL,
    data_type character varying NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.systemconfig OWNER TO postgres;

--
-- Name: telebirrtransaction; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.telebirrtransaction OWNER TO postgres;

--
-- Name: telebirrtransaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.telebirrtransaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.telebirrtransaction_id_seq OWNER TO postgres;

--
-- Name: telebirrtransaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.telebirrtransaction_id_seq OWNED BY public.telebirrtransaction.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public."user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: auditlog id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditlog ALTER COLUMN id SET DEFAULT nextval('public.auditlog_id_seq'::regclass);


--
-- Name: deposittriplink id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposittriplink ALTER COLUMN id SET DEFAULT nextval('public.deposittriplink_id_seq'::regclass);


--
-- Name: driver id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver ALTER COLUMN id SET DEFAULT nextval('public.driver_id_seq'::regclass);


--
-- Name: driverdocument id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driverdocument ALTER COLUMN id SET DEFAULT nextval('public.driverdocument_id_seq'::regclass);


--
-- Name: expectedrevenue id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expectedrevenue ALTER COLUMN id SET DEFAULT nextval('public.expectedrevenue_id_seq'::regclass);


--
-- Name: notification id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification ALTER COLUMN id SET DEFAULT nextval('public.notification_id_seq'::regclass);


--
-- Name: profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles ALTER COLUMN id SET DEFAULT nextval('public.profiles_id_seq'::regclass);


--
-- Name: reconciliationbatch id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reconciliationbatch ALTER COLUMN id SET DEFAULT nextval('public.reconciliationbatch_id_seq'::regclass);


--
-- Name: reconciliationrecord id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reconciliationrecord ALTER COLUMN id SET DEFAULT nextval('public.reconciliationrecord_id_seq'::regclass);


--
-- Name: telebirrtransaction id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telebirrtransaction ALTER COLUMN id SET DEFAULT nextval('public.telebirrtransaction_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: auditlog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auditlog (id, target_type, target_id, field_name, old_value, new_value, user_id, "timestamp") FROM stdin;
\.


--
-- Data for Name: deposittriplink; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deposittriplink (id, transaction_id, trip_id, amount_applied, batch_id, created_at) FROM stdin;
\.


--
-- Data for Name: driver; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver (id, yango_driver_id, name, phone, operator_id, driver_type, shift, reconciliation_start_date, avatar_data, created_at) FROM stdin;
\.


--
-- Data for Name: driverdocument; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driverdocument (id, driver_id, document_type, filename, content_type, file_data, uploaded_at, notes) FROM stdin;
\.


--
-- Data for Name: drivertrip; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.drivertrip (id, short_id, driver_id, status, category, payment_method, price, provider, booked_at, yango_created_at, ended_at, address_from, address_from_lat, address_from_lon, car_id, car_brand_model, car_license, car_callsign, order_type_name, driver_work_rule, passenger_name, mileage, deposited_amount, reconciliation_status, reconciliation_notes, synced_at) FROM stdin;
\.


--
-- Data for Name: expectedrevenue; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expectedrevenue (id, driver_id, date, expected_amount, created_at) FROM stdin;
\.


--
-- Data for Name: notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification (id, title, message, type, is_read, action_url, created_at) FROM stdin;
\.


--
-- Data for Name: order; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."order" (id, short_id, status, price, payment_method, driver_id, driver_name, ended_at, address_from, created_at) FROM stdin;
\.


--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.profiles (id, name, email, age) FROM stdin;
\.


--
-- Data for Name: reconciliationbatch; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reconciliationbatch (id, filename, uploaded_by, total_transactions, total_amount, drivers_matched, trips_reconciled, status, created_at, reversed_at, reversed_by) FROM stdin;
\.


--
-- Data for Name: reconciliationrecord; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reconciliationrecord (id, driver_id, date, expected_amount, actual_amount, status, created_at) FROM stdin;
\.


--
-- Data for Name: systemconfig; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.systemconfig (key, value, description, data_type, updated_at) FROM stdin;
\.


--
-- Data for Name: telebirrtransaction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.telebirrtransaction (id, transaction_id, amount, sender_identifier, merchant_id, "timestamp", status, opposite_party, is_reconciled, driver_id, created_at) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, email, hashed_password, full_name, phone, two_factor_enabled, role, is_active, last_login, created_at) FROM stdin;
\.


--
-- Name: auditlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auditlog_id_seq', 1, false);


--
-- Name: deposittriplink_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deposittriplink_id_seq', 1, false);


--
-- Name: driver_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_id_seq', 1, false);


--
-- Name: driverdocument_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driverdocument_id_seq', 1, false);


--
-- Name: expectedrevenue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expectedrevenue_id_seq', 1, false);


--
-- Name: notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_id_seq', 1, false);


--
-- Name: profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.profiles_id_seq', 1, false);


--
-- Name: reconciliationbatch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reconciliationbatch_id_seq', 1, false);


--
-- Name: reconciliationrecord_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reconciliationrecord_id_seq', 1, false);


--
-- Name: telebirrtransaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.telebirrtransaction_id_seq', 1, false);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 1, false);


--
-- Name: auditlog auditlog_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditlog
    ADD CONSTRAINT auditlog_pkey PRIMARY KEY (id);


--
-- Name: deposittriplink deposittriplink_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_pkey PRIMARY KEY (id);


--
-- Name: driver driver_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver
    ADD CONSTRAINT driver_pkey PRIMARY KEY (id);


--
-- Name: driverdocument driverdocument_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driverdocument
    ADD CONSTRAINT driverdocument_pkey PRIMARY KEY (id);


--
-- Name: drivertrip drivertrip_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.drivertrip
    ADD CONSTRAINT drivertrip_pkey PRIMARY KEY (id);


--
-- Name: expectedrevenue expectedrevenue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expectedrevenue
    ADD CONSTRAINT expectedrevenue_pkey PRIMARY KEY (id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: reconciliationbatch reconciliationbatch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reconciliationbatch
    ADD CONSTRAINT reconciliationbatch_pkey PRIMARY KEY (id);


--
-- Name: reconciliationrecord reconciliationrecord_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reconciliationrecord
    ADD CONSTRAINT reconciliationrecord_pkey PRIMARY KEY (id);


--
-- Name: systemconfig systemconfig_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.systemconfig
    ADD CONSTRAINT systemconfig_pkey PRIMARY KEY (key);


--
-- Name: telebirrtransaction telebirrtransaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telebirrtransaction
    ADD CONSTRAINT telebirrtransaction_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: ix_auditlog_target_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_auditlog_target_id ON public.auditlog USING btree (target_id);


--
-- Name: ix_auditlog_target_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_auditlog_target_type ON public.auditlog USING btree (target_type);


--
-- Name: ix_deposittriplink_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deposittriplink_batch_id ON public.deposittriplink USING btree (batch_id);


--
-- Name: ix_deposittriplink_transaction_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deposittriplink_transaction_id ON public.deposittriplink USING btree (transaction_id);


--
-- Name: ix_deposittriplink_trip_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deposittriplink_trip_id ON public.deposittriplink USING btree (trip_id);


--
-- Name: ix_driver_driver_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_driver_driver_type ON public.driver USING btree (driver_type);


--
-- Name: ix_driver_operator_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_driver_operator_id ON public.driver USING btree (operator_id);


--
-- Name: ix_driver_shift; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_driver_shift ON public.driver USING btree (shift);


--
-- Name: ix_driver_yango_driver_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_driver_yango_driver_id ON public.driver USING btree (yango_driver_id);


--
-- Name: ix_driverdocument_document_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_driverdocument_document_type ON public.driverdocument USING btree (document_type);


--
-- Name: ix_order_driver_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_driver_id ON public."order" USING btree (driver_id);


--
-- Name: ix_order_ended_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_ended_at ON public."order" USING btree (ended_at);


--
-- Name: ix_telebirrtransaction_sender_identifier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_telebirrtransaction_sender_identifier ON public.telebirrtransaction USING btree (sender_identifier);


--
-- Name: ix_telebirrtransaction_transaction_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_telebirrtransaction_transaction_id ON public.telebirrtransaction USING btree (transaction_id);


--
-- Name: ix_user_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_user_email ON public."user" USING btree (email);


--
-- Name: ix_user_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_phone ON public."user" USING btree (phone);


--
-- Name: auditlog auditlog_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditlog
    ADD CONSTRAINT auditlog_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: deposittriplink deposittriplink_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.reconciliationbatch(id);


--
-- Name: deposittriplink deposittriplink_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.telebirrtransaction(transaction_id);


--
-- Name: deposittriplink deposittriplink_trip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposittriplink
    ADD CONSTRAINT deposittriplink_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.drivertrip(id);


--
-- Name: driverdocument driverdocument_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driverdocument
    ADD CONSTRAINT driverdocument_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: drivertrip drivertrip_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.drivertrip
    ADD CONSTRAINT drivertrip_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: expectedrevenue expectedrevenue_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expectedrevenue
    ADD CONSTRAINT expectedrevenue_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: reconciliationbatch reconciliationbatch_reversed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reconciliationbatch
    ADD CONSTRAINT reconciliationbatch_reversed_by_fkey FOREIGN KEY (reversed_by) REFERENCES public."user"(id);


--
-- Name: reconciliationbatch reconciliationbatch_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reconciliationbatch
    ADD CONSTRAINT reconciliationbatch_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public."user"(id);


--
-- Name: reconciliationrecord reconciliationrecord_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reconciliationrecord
    ADD CONSTRAINT reconciliationrecord_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- Name: telebirrtransaction telebirrtransaction_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telebirrtransaction
    ADD CONSTRAINT telebirrtransaction_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id);


--
-- PostgreSQL database dump complete
--

\unrestrict HM07kUkqD3LgLN17mCacpmQaASTZXdqup2o1jPrUhaOOxLfc3bNOv4oOwr5n2bH

