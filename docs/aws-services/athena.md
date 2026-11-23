# Amazon Athena — Hướng dẫn dịch vụ và thực hành

<small>ANALYTICS · SERVERLESS SQL · UC02</small>

## 1. Amazon Athena là gì?

**Amazon Athena** là dịch vụ **serverless interactive query** cho phép chạy SQL trực tiếp trên dữ liệu lưu trong Amazon S3. Người học không cần tạo database server, cài query engine hay quản lý cluster.

Athena thường dùng **AWS Glue Data Catalog** để tra metadata database, table, column, data type và partition. Athena đọc dữ liệu từ S3, thực thi SQL và ghi kết quả vào S3 location cấu hình trong **Workgroup**.

Athena không tự biến file S3 thành table. Cần khai báo metadata bằng DDL, Glue Crawler hoặc công cụ tương thích.

## 2. 10 WH questions

| WH | Nội dung |
|---|---|
| What | Serverless interactive query service hỗ trợ SQL trên dữ liệu S3. |
| Why | Query data lake mà không vận hành query cluster. |
| When | Ad-hoc analysis, exploration, reporting, reconciliation, data quality; không phù hợp OLTP hoặc row updates liên tục. |
| Where | Query thuộc Region; S3 source, query results và Catalog cần cấu hình Region/network hợp lý. |
| Who | Analyst, data engineer, application role; IAM, S3, Glue, KMS và có thể Lake Formation permissions. |
| Which | Workgroup, engine version, output location, encryption, file format, partition strategy và query limits. |
| How | DDL, Glue Crawler, Console, CLI, SDK, JDBC/ODBC; SQL và CTAS. |
| How much | Bytes scanned theo pricing model; cộng S3, Glue, KMS, transfer và optional features. |
| What if | AccessDenied, schema mismatch, malformed input, missing partitions, timeout, scan lớn hoặc output location lỗi. |
| How compared | Athena vs Redshift warehouse vs Glue ETL vs EMR Spark vs RDS/SQL Server OLTP. |

## 3. Architecture

~~~mermaid
flowchart LR
  S3[("S3 Raw / Curated")] --> CAT[("Glue Data Catalog")]
  CAT --> ATH["Athena Query Engine"]
  USER["Analyst / Application Role"] --> ATH
  ATH --> RESULT[("S3 Query Results")]
  LF["Lake Formation"] -. table grants .-> CAT
  IAM["IAM + S3 + KMS policies"] -. authorization .-> ATH
~~~

## 4. Lab: Workgroup và SQL trên S3

Prerequisites: learning account độc lập, S3 bucket private với synthetic CSV và IAM permissions cho Athena, Glue Catalog, source/result S3, KMS/Lake Formation nếu dùng.

### Step 1 — Create Workgroup

1. Athena Console → Workgroups → Create workgroup.
2. Name: `uc-athena-learning`.
3. Chọn supported engine version.
4. Query result location: `s3://<bucket>/athena-results/`.
5. Bật encryption.
6. Cân nhắc Enforce workgroup configuration.
7. Thiết lập bytes-scanned cutoff.
8. Save.

### Step 2 — Create database/table

~~~sql
CREATE DATABASE IF NOT EXISTS learning_analytics;
~~~

~~~sql
CREATE EXTERNAL TABLE IF NOT EXISTS learning_analytics.loan_demo (
  loan_id STRING, product STRING, principal_vnd BIGINT,
  tenor_months INT, dpd INT, default_flag INT, snapshot_date STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar'=',', 'quoteChar'='"', 'escapeChar'='\\\\'
)
STORED AS TEXTFILE
LOCATION 's3://<bucket>/raw/loan_demo/'
TBLPROPERTIES ('skip.header.line.count'='1');
~~~

### Step 3 — Query

~~~sql
SELECT product, COUNT(*) AS accounts, SUM(principal_vnd) AS total_principal
FROM learning_analytics.loan_demo
GROUP BY product ORDER BY total_principal DESC;
~~~

### Step 4 — CTAS Parquet

~~~sql
CREATE TABLE learning_analytics.loan_demo_parquet
WITH (
  format='PARQUET',
  write_compression='SNAPPY',
  external_location='s3://<bucket>/curated/loan_demo_parquet/'
) AS
SELECT loan_id, product, principal_vnd, tenor_months, dpd, default_flag,
       CAST(snapshot_date AS DATE) AS snapshot_date
FROM learning_analytics.loan_demo;
~~~

Target location phải mới/rỗng. `DROP TABLE` không mặc định xóa S3 objects.

## 5. Performance and cost

- Chỉ select cột cần dùng.
- Dùng Parquet/ORC khi phù hợp.
- Partition theo filter thường dùng, ví dụ snapshot date/month.
- Tránh quá nhiều small files và partitions.
- Xem Data scanned, execution time và query plan.
- Dùng Workgroup tách workload, enforce result location và bytes-scanned cutoff.
- Ước tính bytes scanned/query frequency bằng AWS Pricing Calculator.

## 6. Alternatives

| Service | Chọn khi |
|---|---|
| Athena | SQL ad-hoc trên S3, ít vận hành compute |
| Redshift | Data warehouse, concurrent BI, tuned analytics |
| Glue ETL | Transform/cleanse/convert |
| EMR | Spark/Hadoop cần kiểm soát runtime |
| RDS / SQL Server | Transactional application, relational updates |

## 7. Troubleshooting

| Error | Kiểm tra |
|---|---|
| AccessDenied | Athena IAM, S3 source/result, KMS, Lake Formation |
| Table not found | Catalog, database, Region, Workgroup |
| HIVE_BAD_DATA | CSV delimiter, quote, schema, type |
| No output location | Workgroup result config |
| CTAS location not empty | Chọn unique empty prefix |
| Scan too high | Parquet, partition pruning, select columns |

## 8. Cleanup

1. Dừng query còn chạy.
2. `DROP TABLE`/`DROP DATABASE` metadata lab.
3. Xóa S3 test output và versions đúng prefix.
4. Xóa Workgroup nếu không cần.
5. Kiểm tra Billing/Cost Explorer.

## 9. Official references

- [Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
- [Athena Workgroups](https://docs.aws.amazon.com/athena/latest/ug/workgroups-create-update-delete.html)
- [CTAS](https://docs.aws.amazon.com/athena/latest/ug/ctas.html)
- [Athena pricing](https://aws.amazon.com/athena/pricing/)
- [Athena access control](https://docs.aws.amazon.com/athena/latest/ug/security-iam-athena.html)