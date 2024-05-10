DO $$
DECLARE
    i INTEGER := 1;
BEGIN
    WHILE i <= 50 LOOP
        EXECUTE format('DROP VIEW IF EXISTS partition%s', i);
        i := i + 1;
    END LOOP;
END $$;
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