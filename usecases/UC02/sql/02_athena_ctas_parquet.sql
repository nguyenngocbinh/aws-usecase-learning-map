-- UC02 Lab: Convert CSV source to compressed Parquet using Athena CTAS.
-- Replace <bucket-name> with your test bucket.
-- The destination prefix must be empty and dedicated to this CTAS output.

CREATE TABLE uc02_learning.loan_demo_parquet
WITH (
    format = 'PARQUET',
    external_location = 's3://<bucket-name>/curated/loan_demo_parquet/',
    write_compression = 'SNAPPY'
) AS
SELECT
    loan_id,
    product,
    principal_vnd,
    tenor_months,
    dpd,
    default_flag,
    CAST(snapshot_date AS DATE) AS snapshot_date
FROM uc02_learning.loan_demo_csv;

SELECT
    product,
    COUNT(*) AS account_count,
    SUM(principal_vnd) AS total_principal_vnd
FROM uc02_learning.loan_demo_parquet
GROUP BY product;
