DROP TABLE IF EXISTS census;

CREATE TABLE census (
    age INT, 
    workclass VARCHAR, 
    fnlwgt INT, 
    education VARCHAR, 
    education_num INT, 
    marital_status VARCHAR, 
    occupation VARCHAR, 
    relationship VARCHAR, 
    race VARCHAR, 
    sex VARCHAR, 
    capital_gain INT, 
    capital_loss INT, 
    hours_per_week INT, 
    native_country VARCHAR, 
    class VARCHAR
);

-- COPY census FROM '../data/adult-data.csv' WITH CSV;

ALTER TABLE census ADD COLUMN id SERIAL PRIMARY KEY;

CREATE OR REPLACE FUNCTION partition_function(id INT)
RETURNS INT AS $$
BEGIN
    RETURN id % 10;
END;
$$ LANGUAGE plpgsql;