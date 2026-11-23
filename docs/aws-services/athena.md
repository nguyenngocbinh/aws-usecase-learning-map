# Amazon Athena — Hướng dẫn dịch vụ và thực hành

<small>ANALYTICS · SERVERLESS SQL · UC02</small>

## 1. Amazon Athena là gì?

**Amazon Athena** là dịch vụ **serverless interactive query** cho phép chạy SQL trực tiếp trên dữ liệu lưu trong Amazon S3. Người học không cần tạo database server, cài đặt query engine hay quản lý cluster.

Athena thường sử dụng **AWS Glue Data Catalog** để tra cứu metadata như database, table, column, data type và partition. Athena đọc dữ liệu từ S3, thực thi truy vấn và ghi kết quả vào S3 location được cấu hình trong **Workgroup**.

> Athena không tự động biến file trên S3 thành table. Cần khai báo metadata bằng DDL, Glue Crawler hoặc công cụ tương thích Hive metastore.

## 2. Khi nào nên dùng Athena?

- Phân tích ad-hoc dữ liệu CSV, JSON, Parquet, ORC và các định dạng được hỗ trợ.
- Truy vấn Data Lake mà không cần nạp dữ liệu vào database riêng.
- Kiểm tra dữ liệu sau ETL, đối soát record count và data quality.
- Chạy SQL theo lịch hoặc tích hợp với BI/analytics tools.
- Khám phá dữ liệu trước khi xây dựng pipeline production.

Không nên mặc định dùng Athena thay cho SQL Server/OLTP database. Athena phù hợp phân tích dữ liệu trên object storage, không phải transactional database cho ứng dụng cần ghi/cập nhật từng dòng với latency thấp.

## 3. Architecture

### 3.1 Luồng S3 → Glue Data Catalog → Athena

~~~mermaid
flowchart LR
  SRC["Local / On-prem CSV"] --> UP["AWS CLI / Boto3"]
  UP --> RAW["S3 Raw Zone"]
  RAW --> CATALOG["AWS Glue Data Catalog"]
  CATALOG --> ATHENA["Amazon Athena"]
  RAW --> ATHENA
  ATHENA --> RESULT["S3 Query Results"]
  ATHENA -. "Metrics / query history" .-> CW["CloudWatch / Athena Console"]
~~~

### 3.2 Phân biệt dữ liệu và metadata

| Thành phần | Lưu ở đâu? | Vai trò |
|---|---|---|
| Data files | Amazon S3 | Lưu nội dung CSV/Parquet/JSON |
| Database/Table metadata | Glue Data Catalog | Tên bảng, schema, location, partition |
| SQL execution | Athena | Đọc dữ liệu và thực thi SQL |
| Query results | S3 output location | Lưu kết quả truy vấn |
| Access control | IAM, S3 policy, KMS, Lake Formation (nếu dùng) | Kiểm soát ai được query và đọc dữ liệu |

**Lưu ý:** xóa Glue table không đồng nghĩa xóa file dữ liệu trong S3. Ngược lại, xóa file S3 có thể khiến table metadata vẫn tồn tại nhưng query lỗi hoặc thiếu dữ liệu.

## 4. 10 WH questions — Amazon Athena

| WH | Câu hỏi và giải thích |
|---|---|
| What | Athena là serverless SQL query service, đọc dữ liệu trực tiếp từ S3 và trả kết quả truy vấn. |
| Why | Không phải quản lý cluster; triển khai nhanh cho ad-hoc analytics, data exploration và data quality checks. |
| When | Dùng khi dữ liệu đã nằm trên S3 và workload chủ yếu là analytical/read-heavy. Tránh dùng làm OLTP database hoặc workload cần cập nhật từng record liên tục. |
| Where | Query chạy trong AWS Region của Athena; dữ liệu và query result nằm ở S3 location. Nên đặt Athena, Glue Catalog và S3 cùng Region để giảm phức tạp và tránh data transfer không cần thiết. |
| Who | IAM principal/role cần quyền chạy Athena query, truy cập Glue Catalog và đọc data S3; đồng thời cần ghi query result vào S3. Nếu dùng Lake Formation, cần thêm quyền tương ứng. |
| Which | Chọn Workgroup để tách workload, engine version được hỗ trợ, output location, encryption và data format phù hợp. Dùng Parquet/ORC và partitioning cho dữ liệu lớn. |
| How | Tạo database/table bằng DDL hoặc Glue Crawler; chọn Workgroup; chạy SQL qua Console, CLI, SDK hoặc JDBC/ODBC; kiểm tra query execution và result trên S3. |
| How much | Pricing chủ yếu theo bytes scanned với pricing model phổ biến; ngoài ra có thể phát sinh S3 storage/request, Glue Catalog/Crawler, KMS, data transfer và các tính năng bổ sung. Kiểm tra pricing theo Region và Workgroup. |
| What if | Xử lý AccessDenied, sai S3 location, schema mismatch, partition không được nhận diện, file format không hợp lệ, query timeout/limit và chi phí scan cao. |
| How compared | Athena là SQL query serverless trên S3; Redshift phù hợp data warehouse workload; Glue ETL dùng cho data processing; EMR phù hợp Spark/Hadoop cần kiểm soát compute; RDS/SQL Server phù hợp transactional relational workload. |

## 5. So sánh với lựa chọn thay thế

| Dịch vụ | Bản chất | Chọn khi | Trade-off |
|---|---|---|---|
| Amazon Athena | Serverless SQL query trên S3 | Ad-hoc analytics, data exploration, data quality | Hiệu năng/chi phí phụ thuộc data layout và bytes scanned |
| Amazon Redshift | Cloud data warehouse | BI concurrency, warehouse workload, dimensional analytics | Cần thiết kế capacity/serverless configuration và tối ưu warehouse |
| AWS Glue ETL | Serverless data integration/processing | Transform, cleanse, join và ghi curated dataset | Không phải công cụ thay thế cho mọi interactive SQL use case |
| Amazon EMR | Managed big-data platform | Spark/Hadoop và workload cần tùy biến compute | Nhiều quyết định vận hành/capacity hơn |
| Amazon RDS / SQL Server | Managed relational database | OLTP, transaction, row-level updates và application queries | Không phải lựa chọn mặc định cho data lake query quy mô lớn |

**Decision rule:** dữ liệu nằm trên S3 và cần SQL để phân tích → thử Athena; cần ETL biến đổi dữ liệu → Glue; cần warehouse phục vụ BI concurrency → đánh giá Redshift; cần transaction → RDS/SQL Server.

## 6. Prerequisites

- AWS learning account riêng, MFA và Billing Budget/alert.
- Có S3 bucket private, ví dụ bucket tạo trong UC01.
- AWS CLI v2 đã đăng nhập bằng SSO/role.
- Có quyền Athena, Glue Data Catalog và S3 theo least privilege.
- Chỉ sử dụng dữ liệu synthetic trong repository.
- Chọn một Region thống nhất cho S3, Glue và Athena.

### 6.1 Kiểm tra AWS identity

~~~powershell
aws sts get-caller-identity --profile aws-learning
aws configure get region --profile aws-learning
~~~

## 7. Hands-on lab

Lab sử dụng file **usecases/UC01/data/sample_loans.csv** đã upload lên S3 ở UC01.

### Lab 01 — Chuẩn bị S3 prefixes

Tạo các prefix sau trong bucket test:

~~~text
s3://<bucket-name>/
  landing/loan_demo/
    sample_loans.csv
  athena-results/
  curated/loan_demo_parquet/
~~~

Upload file nếu chưa có:

~~~powershell
$env:AWS_PROFILE = "aws-learning"
$env:AWS_REGION = "ap-southeast-1"
$env:BUCKET = "your-unique-bucket-name"

aws s3 cp .\usecases\UC01\data\sample_loans.csv "s3://$env:BUCKET/landing/loan_demo/sample_loans.csv" --region $env:AWS_REGION
~~~

### Lab 02 — Tạo Athena Workgroup

1. Mở [Amazon Athena Console](https://console.aws.amazon.com/athena/).
2. Chọn Workgroups → Create workgroup.
3. Đặt tên **uc02-learning**.
4. Chọn Athena engine version được AWS khuyến nghị/cho phép trong Region.
5. Cấu hình Query result location: **s3://<bucket-name>/athena-results/**.
6. Bật encryption cho query results theo policy của learning account.
7. Nếu phù hợp, bật **Enforce workgroup configuration** để người dùng không ghi đè output location và cấu hình bảo mật.
8. Có thể đặt per-query data usage control để giới hạn bytes scanned; mức giới hạn phải phù hợp với bài lab và pricing hiện hành.
9. Tạo Workgroup.

Không dùng chung Workgroup production. Workgroup giúp tách cấu hình, lịch sử query và cost controls theo nhóm workload.

### Lab 03 — Tạo Glue Data Catalog database và external table

Chọn Workgroup **uc02-learning**, mở Query editor và chạy SQL dưới đây. Thay `&lt;bucket-name&gt;` bằng tên bucket thật.

~~~sql
CREATE DATABASE IF NOT EXISTS uc02_learning;
~~~

Tạo external table đọc CSV:

~~~sql
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
TBLPROPERTIES (
    'skip.header.line.count' = '1'
);
~~~

Kiểm tra schema và dữ liệu:

~~~sql
SHOW TABLES IN uc02_learning;

DESCRIBE uc02_learning.loan_demo_csv;

SELECT *
FROM uc02_learning.loan_demo_csv
LIMIT 10;
~~~

**Chú ý:** nếu prefix có nhiều CSV với schema khác nhau, không đặt tất cả vào cùng một table location. Nên tách prefix theo dataset/table và chuẩn hóa naming convention.

### Lab 04 — Thực hành SQL và Data Quality

Đếm số record:

~~~sql
SELECT COUNT(*) AS row_count
FROM uc02_learning.loan_demo_csv;
~~~

Tổng dư nợ theo product:

~~~sql
SELECT
    product,
    COUNT(*) AS account_count,
    SUM(principal_vnd) AS total_principal_vnd,
    AVG(dpd) AS average_dpd
FROM uc02_learning.loan_demo_csv
GROUP BY product
ORDER BY total_principal_vnd DESC;
~~~

Tỷ lệ default:

~~~sql
SELECT
    product,
    COUNT(*) AS account_count,
    SUM(default_flag) AS default_count,
    CAST(SUM(default_flag) AS DOUBLE)
        / NULLIF(COUNT(*), 0) AS default_rate
FROM uc02_learning.loan_demo_csv
GROUP BY product;
~~~

Kiểm tra dữ liệu bất thường:

~~~sql
SELECT *
FROM uc02_learning.loan_demo_csv
WHERE loan_id IS NULL
   OR principal_vnd < 0
   OR tenor_months <= 0
   OR dpd < 0
   OR default_flag NOT IN (0, 1);
~~~

### Lab 05 — Chuyển CSV sang Parquet bằng CTAS

CSV dễ trao đổi nhưng thường scan nhiều dữ liệu hơn columnar format. Dùng **CTAS (CREATE TABLE AS SELECT)** để tạo dataset Parquet trên S3:

~~~sql
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
~~~

Sau khi CTAS thành công, kiểm tra dữ liệu:

~~~sql
SELECT
    product,
    COUNT(*) AS account_count,
    SUM(principal_vnd) AS total_principal_vnd
FROM uc02_learning.loan_demo_parquet
GROUP BY product;
~~~

**Lưu ý quan trọng:**
- external_location phải là S3 location riêng, rỗng và chưa chứa dữ liệu không liên quan.
- Không chạy lại CTAS vào cùng một location đang chứa output cũ; kiểm tra và dọn dữ liệu test trước khi chạy lại.
- CTAS tạo table metadata và ghi files vào S3. Xóa table metadata không tự động xóa các files.
- Parquet là columnar format; hiệu quả thực tế phụ thuộc column selection, file size, compression, partitioning và query pattern.

## 8. Tối ưu chi phí và hiệu năng

| Kỹ thuật | Tác dụng | Cách thực hiện |
|---|---|---|
| Chọn đúng cột | Giảm dữ liệu cần đọc | Tránh SELECT * trên bảng lớn |
| Parquet/ORC | Columnar storage, compression | Dùng CTAS hoặc Glue ETL |
| Partitioning | Bỏ qua partition không liên quan | Partition theo ngày/tháng hoặc business dimension phù hợp |
| File sizing | Hạn chế quá nhiều file nhỏ | Compact files trong ETL |
| Workgroup controls | Tách workload và giới hạn query | Workgroup, bytes scanned controls |
| Query review | Phát hiện query scan lớn | Xem query details và bytes scanned |

Ví dụ partition pruning (áp dụng khi tạo bảng partitioned):

~~~sql
SELECT COUNT(*)
FROM uc02_learning.loan_demo_partitioned
WHERE snapshot_month = '2026-09';
~~~

Chỉ dùng partition key có ích cho query pattern. Quá nhiều partition hoặc file nhỏ có thể làm tăng metadata overhead và giảm hiệu năng.

## 9. Security và IAM permissions

Một query thường cần các quyền theo nhóm:

- Athena: tạo/chạy query và xem query execution trong Workgroup.
- Glue Data Catalog: đọc database/table metadata; quyền tạo/sửa metadata nếu người dùng thực hiện DDL.
- S3 source: **s3:ListBucket** có điều kiện prefix phù hợp và **s3:GetObject** trên data prefix.
- S3 query results: **s3:PutObject**, và quyền đọc/xóa nếu workflow cần.
- KMS: quyền sử dụng key tương ứng nếu source/result được mã hóa bằng SSE-KMS.
- Lake Formation: bổ sung grant khi Data Catalog được quản trị bằng Lake Formation.

Không cấp **s3:*** trên toàn account chỉ để làm lab chạy được. Phân biệt quyền đọc source data với quyền ghi query results. Thực tế quyền cần thiết còn phụ thuộc thao tác SQL, Workgroup, encryption và cơ chế quản trị Catalog.

## 10. Troubleshooting

| Symptom | Nguyên nhân thường gặp | Hướng kiểm tra |
|---|---|---|
| AccessDenied | Thiếu Athena, Glue, S3 hoặc KMS permission | Kiểm tra IAM, bucket policy, key policy và Lake Formation |
| HIVE_BAD_DATA | CSV không khớp schema/format | Kiểm tra delimiter, quote, encoding và data type |
| Table not found | Chưa tạo database/table hoặc chọn Catalog sai | SHOW DATABASES, SHOW TABLES |
| No output location | Workgroup chưa có result location | Cấu hình S3 output location |
| Location is not empty | CTAS target prefix đã có object | Dùng prefix mới hoặc dọn đúng test output |
| Query scan quá lớn | CSV, SELECT *, thiếu partition pruning | Chọn cột, Parquet, partition |
| Query không thấy file mới | Metadata/partition chưa cập nhật hoặc sai S3 path | Kiểm tra table location và partition metadata |

## 11. Cleanup

Chỉ thực hiện trên learning account và test bucket đã xác minh.

1. Dừng query đang chạy.
2. Xóa table metadata nếu không cần giữ:

~~~sql
DROP TABLE IF EXISTS uc02_learning.loan_demo_parquet;
DROP TABLE IF EXISTS uc02_learning.loan_demo_csv;
DROP DATABASE IF EXISTS uc02_learning;
~~~

3. Xóa query results và curated Parquet files trong đúng prefix test.
4. Nếu cần, xóa Workgroup **uc02-learning**.
5. Không xóa raw file UC01 nếu còn dùng cho bài S3.
6. Kiểm tra S3 versions, incomplete multipart uploads và Billing/Cost Explorer.

**DROP TABLE** không đảm bảo xóa file trên S3. Việc xóa object là destructive; phải xác minh bucket/prefix trước khi thực hiện.

## 12. Knowledge check

1. Athena đọc dữ liệu ở đâu và lưu query result ở đâu?
2. Glue Data Catalog lưu dữ liệu hay metadata?
3. Vì sao cần tạo Workgroup?
4. Athena khác SQL Server ở điểm nào?
5. Vì sao SELECT * có thể làm query đắt hơn?
6. Parquet khác CSV như thế nào?
7. Partitioning giúp giảm bytes scanned ra sao?
8. Xóa Glue table có xóa file S3 không?
9. Một query cần những nhóm IAM permissions nào?
10. Khi nào nên chuyển workload từ Athena sang Redshift hoặc Glue ETL?

## 13. Official references

- [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
- [Athena pricing](https://aws.amazon.com/athena/pricing/)
- [Athena Workgroups](https://docs.aws.amazon.com/athena/latest/ug/workgroups-create-update-delete.html)
- [Querying data in Amazon S3](https://docs.aws.amazon.com/athena/latest/ug/querying.html)
- [Athena data formats](https://docs.aws.amazon.com/athena/latest/ug/columnar-storage.html)
- [CTAS](https://docs.aws.amazon.com/athena/latest/ug/ctas.html)
- [Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html)
- [Athena access control](https://docs.aws.amazon.com/athena/latest/ug/security-iam-athena.html)
- [AWS Pricing Calculator](https://calculator.aws/)

**Last reviewed:** 2026-11-23. Kiểm tra lại engine version, Region availability, quotas, permissions và pricing trước khi chạy lab.
