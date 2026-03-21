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

CREATE TABLE public.dish_ingredients (
    dish_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    qty numeric(6,2) NOT NULL,
    unit_id integer NOT NULL,
    CONSTRAINT dish_ingredients_qty_check CHECK ((qty > (0)::numeric))
);


ALTER TABLE public.dish_ingredients OWNER TO postgres;

CREATE TABLE public.dish_type (
    id integer NOT NULL,
    type_name character varying(100) NOT NULL
);


ALTER TABLE public.dish_type OWNER TO postgres;

CREATE SEQUENCE public.dish_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dish_type_id_seq OWNER TO postgres;


ALTER SEQUENCE public.dish_type_id_seq OWNED BY public.dish_type.id;

CREATE TABLE public.dishes (
    id integer NOT NULL,
    recipe_id integer NOT NULL,
    kcal integer NOT NULL,
    carbs_g integer NOT NULL,
    protein_g integer NOT NULL,
    fat_g integer NOT NULL,
    dish_type_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.dishes OWNER TO postgres;

CREATE SEQUENCE public.dishes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dishes_id_seq OWNER TO postgres;

ALTER SEQUENCE public.dishes_id_seq OWNED BY public.dishes.id;

CREATE TABLE public.ingredient_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.ingredient_categories OWNER TO postgres;

CREATE TABLE public.ingredients (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    category_id integer
);


ALTER TABLE public.ingredients OWNER TO postgres;

CREATE TABLE public.recipes (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    recipe_text text NOT NULL,
    photo_path character varying(255) NOT NULL,
    difficulty smallint NOT NULL,
    prep_time smallint NOT NULL,
    CONSTRAINT recipes_difficulty_check CHECK (((difficulty >= 1) AND (difficulty <= 3))),
    CONSTRAINT recipes_prep_time_check CHECK (((prep_time >= 1) AND (prep_time <= 3)))
);


ALTER TABLE public.recipes OWNER TO postgres;

CREATE TABLE public.units (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.units OWNER TO postgres;

CREATE VIEW public.full_dishes_view AS
 SELECT d.id,
    r.name AS dish_name,
    dt.type_name AS dish_type,
    d.kcal,
    d.protein_g,
    d.carbs_g,
    d.fat_g,
    r.recipe_text,
    r.photo_path,
    r.difficulty,
    r.prep_time,
    json_agg(json_build_object('name', i.name, 'qty', di.qty, 'unit', u.name, 'type', ic.name)) AS ingredients
   FROM ((((((public.dishes d
     JOIN public.recipes r ON ((d.recipe_id = r.id)))
     JOIN public.dish_type dt ON ((d.dish_type_id = dt.id)))
     JOIN public.dish_ingredients di ON ((di.dish_id = d.id)))
     JOIN public.ingredients i ON ((di.ingredient_id = i.id)))
     JOIN public.ingredient_categories ic ON ((i.category_id = ic.id)))
     JOIN public.units u ON ((di.unit_id = u.id)))
  GROUP BY d.id, r.name, dt.type_name, d.kcal, d.protein_g, d.carbs_g, d.fat_g, r.recipe_text, r.photo_path, r.difficulty, r.prep_time;


ALTER VIEW public.full_dishes_view OWNER TO postgres;

CREATE SEQUENCE public.ingredient_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ingredient_categories_id_seq OWNER TO postgres;

ALTER SEQUENCE public.ingredient_categories_id_seq OWNED BY public.ingredient_categories.id;

CREATE SEQUENCE public.ingredients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ingredients_id_seq OWNER TO postgres;

ALTER SEQUENCE public.ingredients_id_seq OWNED BY public.ingredients.id;

CREATE SEQUENCE public.recipes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipes_id_seq OWNER TO postgres;

ALTER SEQUENCE public.recipes_id_seq OWNED BY public.recipes.id;

CREATE SEQUENCE public.units_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.units_id_seq OWNER TO postgres;

ALTER SEQUENCE public.units_id_seq OWNED BY public.units.id;

ALTER TABLE ONLY public.dish_type ALTER COLUMN id SET DEFAULT nextval('public.dish_type_id_seq'::regclass);

ALTER TABLE ONLY public.dishes ALTER COLUMN id SET DEFAULT nextval('public.dishes_id_seq'::regclass);

ALTER TABLE ONLY public.ingredient_categories ALTER COLUMN id SET DEFAULT nextval('public.ingredient_categories_id_seq'::regclass);

ALTER TABLE ONLY public.ingredients ALTER COLUMN id SET DEFAULT nextval('public.ingredients_id_seq'::regclass);

ALTER TABLE ONLY public.recipes ALTER COLUMN id SET DEFAULT nextval('public.recipes_id_seq'::regclass);

ALTER TABLE ONLY public.units ALTER COLUMN id SET DEFAULT nextval('public.units_id_seq'::regclass);

ALTER TABLE ONLY public.dish_type
    ADD CONSTRAINT dish_type_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.dish_type
    ADD CONSTRAINT dish_type_type_name_key UNIQUE (type_name);

ALTER TABLE ONLY public.dishes
    ADD CONSTRAINT dishes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.ingredient_categories
    ADD CONSTRAINT ingredient_categories_name_key UNIQUE (name);

ALTER TABLE ONLY public.ingredient_categories
    ADD CONSTRAINT ingredient_categories_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_name_key UNIQUE (name);

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.dish_ingredients
    ADD CONSTRAINT pk_dish_ingredient PRIMARY KEY (dish_id, ingredient_id);

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.dishes
    ADD CONSTRAINT uc_dishes UNIQUE (recipe_id, kcal);

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_name_key UNIQUE (name);

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.dishes
    ADD CONSTRAINT fk_dish_type FOREIGN KEY (dish_type_id) REFERENCES public.dish_type(id);

ALTER TABLE ONLY public.dish_ingredients
    ADD CONSTRAINT fk_dishes FOREIGN KEY (dish_id) REFERENCES public.dishes(id);

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT fk_ingredient_categories FOREIGN KEY (category_id) REFERENCES public.ingredient_categories(id);

ALTER TABLE ONLY public.dish_ingredients
    ADD CONSTRAINT fk_ingredients FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id);

ALTER TABLE ONLY public.dishes
    ADD CONSTRAINT fk_recipe FOREIGN KEY (recipe_id) REFERENCES public.recipes(id);

ALTER TABLE ONLY public.dish_ingredients
    ADD CONSTRAINT fk_units FOREIGN KEY (unit_id) REFERENCES public.units(id);



