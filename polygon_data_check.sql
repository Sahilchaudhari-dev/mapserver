--
-- PostgreSQL database dump
--

\restrict IjJnVLRaHnQbIVFJQYgIyqAliPj4X1ited3gg4jpSMnCZFZYX2mZlBBCb3GMw1E

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4 (Ubuntu 18.4-0ubuntu0.26.04.1)

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

--
-- Data for Name: planet_osm_polygon; Type: TABLE DATA; Schema: public; Owner: geouser
--

COPY public.planet_osm_polygon (osm_id, access, "addr:housename", "addr:housenumber", "addr:interpolation", admin_level, aerialway, aeroway, amenity, area, barrier, bicycle, brand, bridge, boundary, building, construction, covered, culvert, cutting, denomination, disused, embankment, foot, "generator:source", harbour, highway, historic, horse, intermittent, junction, landuse, layer, leisure, lock, man_made, military, motorcar, name, "natural", office, oneway, operator, place, population, power, power_source, public_transport, railway, ref, religion, route, service, shop, sport, surface, toll, tourism, "tower:type", tracktype, tunnel, water, waterway, wetland, width, wood, z_order, way_area, tags, way) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

\unrestrict IjJnVLRaHnQbIVFJQYgIyqAliPj4X1ited3gg4jpSMnCZFZYX2mZlBBCb3GMw1E

