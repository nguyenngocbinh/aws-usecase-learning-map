-- UC02 Lab: Create Glue Data Catalog database and Athena external table.
-- Replace <bucket-name> with the bucket used in your AWS learning account.
-- Source: synthetic sample_loans.csv from UC01.

CREATE DATABASE IF NOT EXISTS uc02_learning;

CREATE EXTERNAL TABLE IF NOT EXISTS uc02_learning.loan_demo_csv (
    loan_id STRING,
    product STRING,
    principal_vnd BIGINT,
    tenor_months INT,
    dpd INT,
    default_flag INT,
    snapshot_date STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'escapeChar' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<bucket-name>/landing/loan_demo/'
TBLPROPERTIES ('skip.header.line.count' = '1');

SHOW TABLES IN uc02_learning;
DESCRIBE uc02_learning.loan_demo_csv;

SELECT COUNT(*) AS row_count
FROM uc02_learning.loan_demo_csv;

SELECT
    product,
    COUNT(*) AS account_count,
    SUM(principal_vnd) AS total_principal_vnd,
    AVG(dpd) AS average_dpd
FROM uc02_learning.loan_demo_csv
GROUP BY product
ORDER BY total_principal_vnd DESC;
