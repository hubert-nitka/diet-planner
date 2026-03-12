CREATE TABLE recipes (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	recipe_text TEXT NOT NULL,
	photo_path VARCHAR(255) NOT NULL,
	difficulty SMALLINT NOT NULL CHECK (difficulty >= 1 AND difficulty <=3),
	prep_time SMALLINT NOT NULL CHECK (prep_time >= 1 AND prep_time <=3)
);

CREATE TABLE dishes (
	id SERIAL PRIMARY KEY,
	recipe_id INTEGER NOT NULL,
	kcal INTEGER NOT NULL,
	carbs_g INTEGER NOT NULL,
	protein_g INTEGER NOT NULL,
	fat_g INTEGER NOT NULL,
	dish_type_id INTEGER NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT uc_dishes UNIQUE (recipe_id, kcal)
);

CREATE TABLE dish_type (
	id SERIAL PRIMARY KEY,
	type_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ingredients (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL UNIQUE,
	category_id INTEGER NOT NULL
);

CREATE TABLE ingredient_categories (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE units (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE dish_ingredients (
	dish_id INTEGER NOT NULL,
	ingredient_id INTEGER NOT NULL,
	qty DECIMAL(6,2) NOT NULL CHECK (qty > 0),
	unit_id INTEGER NOT NULL,
	CONSTRAINT pk_dish_ingredient PRIMARY KEY (dish_id, ingredient_id)
);

ALTER TABLE dishes
ADD CONSTRAINT fk_dish_type
FOREIGN KEY (dish_type_id)
REFERENCES dish_type(id);

ALTER TABLE dish_ingredients
ADD CONSTRAINT fk_dishes
FOREIGN KEY (dish_id)
REFERENCES dishes(id);

ALTER TABLE dish_ingredients
ADD CONSTRAINT fk_ingredients
FOREIGN KEY (ingredient_id)
REFERENCES ingredients(id);

ALTER TABLE dish_ingredients
ADD CONSTRAINT fk_units
FOREIGN KEY (unit_id)
REFERENCES units(id);

ALTER TABLE ingredients
ADD CONSTRAINT fk_ingredient_categories
FOREIGN KEY (category_id)
REFERENCES ingredient_categories(id);

ALTER TABLE dishes
ADD CONSTRAINT fk_recipe
FOREIGN KEY (recipe_id)
REFERENCES recipes(id);