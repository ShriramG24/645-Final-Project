DROP VIEW IF EXISTS partition0;
DROP VIEW IF EXISTS partition1;
DROP VIEW IF EXISTS partition2;
DROP VIEW IF EXISTS partition3;
DROP VIEW IF EXISTS partition4;
DROP VIEW IF EXISTS partition5;
DROP VIEW IF EXISTS partition6;
DROP VIEW IF EXISTS partition7;
DROP VIEW IF EXISTS partition8;
DROP VIEW IF EXISTS partition9;
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