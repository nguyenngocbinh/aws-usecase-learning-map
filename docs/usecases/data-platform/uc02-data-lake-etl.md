# UC02 — Xây dựng Data Lake và ETL

> **UC02 · DATA PLATFORM · HANDS-ON LAB**
>
> Bài thực hành chuyển hóa kiến trúc Raw–Prepared–Curated, Glue, Lake Formation, DataSync và Athena trong tài liệu AWS UAT v1.6 thành lab độc lập. Chỉ dùng synthetic data và learning account; không deploy vào TPBank account.

## 1. Business scenario

Nhóm Data Engineering cần ingest dữ liệu từ On-Premises hoặc file landing vào Amazon S3, chuẩn hóa bằng AWS Glue, quản lý metadata trong Glue Data Catalog, query bằng Athena và kiểm soát truy cập bằng IAM/Lake Formation.

Dataset mẫu là synthetic loan portfolio: `loan_id`, `product`, `principal_vnd`, `tenor_months`, `dpd`, `default_flag`, `snapshot_date`.

## 2. Learning objectives

- Thiết kế Raw, Prepared, Curated zones trong S3.
- Hiểu Glue Data Catalog, Glue Crawler, Glue ETL và Athena.
- Tạo database/table, partition và query dataset.
- Chuyển CSV thành Parquet, tối ưu bytes scanned.
- Hiểu Lake Formation và IAM permissions.
- Xử lý lỗi, quan sát logs/metrics và cleanup.

## 3. Architecture

~~~mermaid
flowchart LR
  SRC["On-Prem DB / Synthetic CSV"] --> ING["DataSync / CLI / SDK"]
  ING --> RAW[("S3 Raw")]
  RAW --> CRAW["Glue Crawler"]
  CRAW --> CAT[("Glue Data Catalog")]
  RAW --> ETL["AWS Glue ETL"]
  ETL --> PREP[("S3 Prepared")]
  PREP --> CAT
  ETL --> CUR[("S3 Curated · Parquet")]
  CUR --> CAT
  CAT --> ATH["Amazon Athena"]
  LF["Lake Formation"] -. grants .-> CAT
  IAM["IAM Role + S3/KMS policies"] -. authorization .-> ETL
  IAM -. authorization .-> ATH
  ATH --> RES[("S3 Query Results")]
  CW["CloudWatch Logs / Metrics"] -. observe .-> ETL
~~~

### 3.1 Data layout

~~~text
s3://<data-bucket>/
  raw/loan_demo/snapshot_date=2026-09-30/part-000.csv
  prepared/loan_demo/snapshot_date=2026-09-30/part-000.parquet
  curated/loan_demo/product=auto/snapshot_date=2026-09-30/part-000.parquet
  athena-results/
  glue-scripts/
~~~

Raw giữ dữ liệu ingest gốc; Prepared chuẩn hóa/schema; Curated phục vụ analytics. Athena results cần prefix riêng, encryption và lifecycle.

## 4. Thành phần và 10 WH

### 4.1 Amazon S3

| WH | Nội dung |
|---|---|
| What | Object storage lưu object trong bucket. |
| Why | Data Lake storage tách rời compute, scale và tích hợp Glue/Athena. |
| When | Landing, raw/curated files, logs, artifacts; không thay database transaction. |
| Where | Chọn Region theo data residency, availability và latency. |
| Who | IAM roles, workload roles, bucket policies, access points. |
| Which | Standard, Intelligent-Tiering, IA, Glacier theo access/retention và minimum duration. |
| How | Console, CLI, SDK, DataSync và Terraform. |
| How much | Storage, requests, retrieval, transfer, lifecycle, replication, KMS. |
| What if | AccessDenied, wrong prefix, overwrite, versioning, incomplete multipart, KMS errors. |
| How compared | S3 object; EBS block; EFS/FSx file; DataSync transfer. |

### 4.2 AWS Glue

| WH | Nội dung |
|---|---|
| What | Serverless data integration gồm Data Catalog, Crawlers và ETL Jobs. |
| Why | Discovery metadata, schema cataloging, transform và data preparation. |
| When | Batch ETL, format conversion, schema normalization. |
| Where | Job, Catalog, connections và target data cần xét Region/network boundaries. |
| Who | Data Engineer, Glue service role, Catalog admin và data consumer. |
| Which | Visual/Script ETL, Spark/Python Shell theo workload; Glue version/worker theo dependency và scale. |
| How | IAM role, script, job, parameters, connection, trigger và monitoring. |
| How much | Worker/DPU runtime, crawler/catalog usage, data transfer và features. |
| What if | Timeout, schema mismatch, permission, dependency, skew, small files, bookmark issues. |
| How compared | Glue managed ETL; EMR cho Spark/Hadoop control; Lambda cho event nhỏ; Step Functions orchestration. |

### 4.3 Glue Data Catalog và Crawler

| WH | Nội dung |
|---|---|
| What | Metadata catalog gồm database, table, schema, partition và location. |
| Why | Cung cấp metadata cho Athena/Glue/analytics engines. |
| When | Cần schema discovery/metadata sharing cho S3 datasets. |
| Where | Catalog có Region scope; cross-account sharing cần thiết kế riêng. |
| Who | Catalog admins, crawler role, ETL roles, Athena users. |
| Which | Crawler tự discovery; DDL/Glue API cho schema governance chặt hơn. |
| How | Chọn S3 target, IAM role, database, schedule rồi chạy crawler hoặc DDL/API. |
| How much | Kiểm tra crawler runtime, catalog requests và feature pricing. |
| What if | Crawler tạo table sai, schema drift, duplicate table, partition không refresh. |
| How compared | Catalog là metadata; S3 là data; Lake Formation là permissions; Athena là query engine. |

### 4.4 Lake Formation

| WH | Nội dung |
|---|---|
| What | Dịch vụ quản trị quyền truy cập Data Lake trên Data Catalog/S3. |
| Why | Centralized fine-grained permissions cho database/table/column và các control được hỗ trợ. |
| When | Nhiều producer/consumer hoặc cần governance tập trung. |
| Where | Cấu hình theo account/Region và registered data locations. |
| Who | Data lake admins, data owners, principals, service roles. |
| Which | IAM-only hay Lake Formation permissions; hiểu hybrid access mode nếu dùng. |
| How | Register S3 location, grant database/table permissions, cấu hình admins. |
| How much | Xác minh pricing hiện hành; còn có S3/Glue/Athena/KMS costs. |
| What if | IAM allow nhưng Lake Formation deny, resource link sai, location chưa register hoặc role thiếu quyền. |
| How compared | IAM quản API/identity; S3 policy bảo vệ object; Lake Formation cấp data permissions qua integrated services. |

### 4.5 Amazon Athena

| WH | Nội dung |
|---|---|
| What | Serverless SQL query service đọc dữ liệu từ S3. |
| Why | Query nhanh mà không cần vận hành cluster. |
| When | Ad-hoc analytics, exploration, reconciliation, data quality; không dùng làm OLTP. |
| Where | Query chạy trong Region; S3 source/result và Catalog cần phù hợp. |
| Who | IAM principal cần Athena, Glue, S3, KMS và có thể Lake Formation. |
| Which | Workgroup, engine version, output location, encryption, format và partition. |
| How | DDL/CTAS, Console, CLI, SDK, JDBC/ODBC. |
| How much | Pricing theo bytes scanned theo mô hình phổ biến; cộng S3, Glue, KMS, transfer. |
| What if | AccessDenied, malformed data, wrong location, missing partitions, timeout, scan lớn. |
| How compared | Athena serverless query; Redshift warehouse; Glue ETL; EMR Spark; RDS/SQL Server OLTP. |

## 5. Alternatives và decision matrix

| Nhu cầu | Service ưu tiên đánh giá | Alternative | Tiêu chí |
|---|---|---|---|
| On-prem → S3 transfer | DataSync | CLI/SDK, Transfer Family, Snow Family | Volume, protocol, network, schedule |
| Object Data Lake | S3 | EFS/FSx | Object API hay file protocol |
| Managed ETL | Glue | EMR, Lambda, ECS | Transform complexity, runtime, control |
| Metadata discovery | Glue Crawler | DDL/Glue API | Auto-discovery hay schema contract |
| Fine-grained access | Lake Formation | IAM/S3 policies | Governance và service integration |
| SQL on S3 | Athena | Redshift, EMR, Trino | Concurrency, latency, cost |
| Orchestration | Step Functions / Glue Workflows | MWAA / EventBridge Scheduler | DAG complexity, retry, Airflow needs |

## 6. Prerequisites

- AWS learning account riêng, MFA và Billing Budget/alert.
- AWS CLI v2 đăng nhập bằng SSO/role.
- S3 bucket private từ UC01 hoặc bucket test mới.
- Synthetic dataset trong repository.
- Một Region thống nhất cho S3, Glue và Athena.
- IAM roles cho Glue Job/Crawler và Athena user.

~~~powershell
aws sts get-caller-identity --profile aws-learning
aws configure get region --profile aws-learning
aws s3 ls --profile aws-learning
~~~

## 7. Hands-on lab A — Data Lake và Athena

### Step 1 — Upload raw CSV

~~~powershell
$env:AWS_PROFILE = "aws-learning"
$env:AWS_REGION = "ap-southeast-1"
$env:BUCKET = "your-unique-learning-bucket"
aws s3 cp .\usecases\UC01\data\sample_loans.csv "s3://$env:BUCKET/raw/loan_demo/sample_loans.csv"
~~~

S3 không có directory thực; prefix xuất hiện khi object key được ghi.

### Step 2 — Tạo Athena Workgroup

1. Athena Console → Workgroups → Create workgroup.
2. Name: `uc02-learning`.
3. Chọn supported engine version.
4. Query result location: `s3://<bucket>/athena-results/`.
5. Bật encryption.
6. Cân nhắc Enforce workgroup configuration.
7. Thiết lập bytes-scanned cutoff phù hợp lab.
8. Create workgroup.

### Step 3 — Tạo Glue Data Catalog database

~~~sql
CREATE DATABASE IF NOT EXISTS uc02_learning;
~~~

### Step 4 — Tạo table từ CSV

Thay `<bucket>` bằng bucket thật:

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
    'escapeChar' = '\\\\'
)
STORED AS TEXTFILE
LOCATION 's3://<bucket>/raw/loan_demo/'
TBLPROPERTIES ('skip.header.line.count'='1');
~~~

Kiểm tra:

~~~sql
SHOW TABLES IN uc02_learning;
DESCRIBE uc02_learning.loan_demo_csv;
SELECT * FROM uc02_learning.loan_demo_csv LIMIT 10;
~~~

Nếu schema sai, kiểm tra delimiter, header, quoting, type và location. Không gộp CSV khác schema vào cùng location.

### Step 5 — SQL analytics và data quality

~~~sql
SELECT product, COUNT(*) AS account_count,
       SUM(principal_vnd) AS total_principal_vnd,
       AVG(dpd) AS average_dpd, SUM(default_flag) AS default_count
FROM uc02_learning.loan_demo_csv
GROUP BY product ORDER BY total_principal_vnd DESC;
~~~

~~~sql
SELECT * FROM uc02_learning.loan_demo_csv
WHERE loan_id IS NULL OR principal_vnd < 0 OR tenor_months <= 0
   OR dpd < 0 OR default_flag NOT IN (0, 1);
~~~

### Step 6 — CSV → Parquet bằng CTAS

~~~sql
CREATE TABLE uc02_learning.loan_demo_parquet
WITH (
  format = 'PARQUET',
  external_location = 's3://<bucket>/curated/loan_demo_parquet/',
  write_compression = 'SNAPPY'
) AS
SELECT loan_id, product, principal_vnd, tenor_months, dpd, default_flag,
       CAST(snapshot_date AS DATE) AS snapshot_date
FROM uc02_learning.loan_demo_csv;
~~~

Target location phải mới/rỗng. Ghi nhận Data scanned ở Query details; dataset nhỏ có thể không cho thấy chênh lệch đáng kể. `DROP TABLE` xóa Catalog metadata, không mặc định xóa S3 files.

## 8. Hands-on lab B — Glue Crawler

1. Glue Console → Data Catalog → Crawlers → Create crawler.
2. Chọn S3 source `s3://<bucket>/raw/loan_demo/`.
3. Tạo/Chọn IAM role chỉ đọc đúng prefix và ghi Catalog metadata.
4. Chọn database `uc02_learning`.
5. Chạy On demand cho lab.
6. Run crawler và đợi trạng thái Succeeded.
7. Kiểm tra table/schema/location trong Data Catalog.
8. Query table bằng Athena.

Crawler phù hợp discovery nhanh. Với production schema contract, cân nhắc DDL/Glue API/IaC để chủ động naming, data types, partition và change control.

## 9. Hands-on lab C — Glue ETL Job

Mục tiêu: đọc CSV từ Raw, validate schema tối thiểu và ghi Parquet vào Prepared. Script PySpark minh họa:

~~~python
import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME", "SOURCE_PATH", "TARGET_PATH"])
sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

source_df = (spark.read.option("header", "true").option("mode", "FAILFAST")
             .csv(args["SOURCE_PATH"]))
required = {"loan_id", "product", "principal_vnd", "tenor_months", "dpd", "default_flag", "snapshot_date"}
missing = required.difference(source_df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

clean_df = (source_df
    .withColumn("principal_vnd", F.col("principal_vnd").cast("long"))
    .withColumn("tenor_months", F.col("tenor_months").cast("int"))
    .withColumn("dpd", F.col("dpd").cast("int"))
    .withColumn("default_flag", F.col("default_flag").cast("int"))
    .withColumn("snapshot_date", F.to_date("snapshot_date"))
    .filter(F.col("loan_id").isNotNull())
    .filter(F.col("principal_vnd") >= 0)
    .filter(F.col("tenor_months") > 0)
    .filter(F.col("dpd") >= 0))
invalid = clean_df.filter(~F.col("default_flag").isin(0, 1)).limit(1).count()
if invalid:
    raise ValueError("default_flag must be 0 or 1")

(clean_df.write.mode("overwrite").format("parquet")
 .option("compression", "snappy")
 .partitionBy("snapshot_date")
 .save(args["TARGET_PATH"]))
job.commit()
~~~

Console configuration:
1. Glue → ETL Jobs → Script editor → Spark.
2. Upload script vào S3 `glue-scripts/`.
3. Chọn Glue version/worker phù hợp và IAM service role.
4. Job arguments: `--SOURCE_PATH=s3://<bucket>/raw/loan_demo/`, `--TARGET_PATH=s3://<bucket>/prepared/loan_demo/`.
5. Role cần `GetObject` raw, `PutObject` prepared, CloudWatch Logs và KMS nếu dùng.
6. Run Job; xem Job Run details và CloudWatch logs.
7. Tạo/refresh Crawler hoặc khai báo table cho Prepared.
8. Query output bằng Athena.

`overwrite` có thể thay đổi output. Production nên dùng run-specific output, atomic publish, retention và rollback thay vì overwrite trực tiếp Curated.

## 10. Hands-on lab D — Lake Formation permissions

Optional vì Lake Formation có thể ảnh hưởng quyền Data Catalog và S3 của principals trong account.

1. Dùng dedicated learning account.
2. Xác định Data Lake administrator và data owner.
3. Register đúng S3 location với role phù hợp.
4. Grant quyền database/table cho consumer principal.
5. Đảm bảo IAM principal cũng có quyền gọi AWS APIs cần thiết.
6. Query Athena với principal được grant.
7. Query với principal không được grant; xác nhận AccessDenied.
8. Thu hồi grants sau lab.

Không thay đổi default Data Lake settings của account dùng chung. Trước lab phải hiểu IAMAllowedPrincipals, hybrid access mode, resource links và Lake Formation registration.

## 11. IAM permission matrix

| Principal | S3 Raw | S3 Prepared/Curated | Glue Catalog | Glue Job | Athena |
|---|---|---|---|---|---|
| Ingestion role | PutObject | Không mặc định | Không mặc định | Không | Không |
| Glue Job role | GetObject | PutObject | Read/Update cần thiết | Run/Read theo orchestration | Không |
| Crawler role | List/Get | Theo target | Create/Update table | Không | Không |
| Analyst role | GetObject theo governance | GetObject theo governance | Get metadata | Không | Query + write result |
| Lake Formation admin | Theo governance design | Theo governance design | Admin/grants | Không mặc định | Không mặc định |

Không cấp `s3:*` trên toàn account chỉ để lab chạy được. Quyền thực tế phụ thuộc query, Workgroup, encryption và governance mode.

## 12. Orchestration: S3 → SQS → Lambda → Glue

Tài liệu UAT mô tả S3 notification → SQS → Lambda → Glue ETL. Pattern này cần idempotency, retry và DLQ.

~~~mermaid
flowchart LR
  UP["S3 Object Created"] --> NOTI["S3 Event Notification"]
  NOTI --> Q["SQS Queue"]
  Q --> L["Lambda Trigger"]
  L --> JOB["Start Glue Job"]
  JOB --> OUT["Prepared / Curated S3"]
  Q -. retries exhausted .-> DLQ["Dead Letter Queue"]
  DLQ --> ALARM["CloudWatch Alarm / SNS"]
~~~

- Event delivery có thể lặp; không giả định exactly-once.
- Dùng object key/version hoặc event identity làm idempotency key.
- Thiết kế visibility timeout và retry phù hợp.
- Lambda khởi tạo/điều phối job, không giữ execution lâu.
- Cấu hình DLQ, redrive và alarm.
- Dùng Glue Workflow, Step Functions hoặc MWAA khi dependency phức tạp.

## 13. Cost and performance

| Driver | Biện pháp |
|---|---|
| S3 storage | Lifecycle/retention đúng nhu cầu; xóa test objects/versions |
| Athena bytes scanned | Parquet/ORC, projection, select columns, partition pruning, Workgroup cutoff |
| Glue worker runtime | Chọn worker phù hợp, filter sớm, xử lý skew/small files |
| Crawler | Chạy On demand/schedule hợp lý; giới hạn scope |
| KMS | Theo dõi key/request costs nếu SSE-KMS |
| SQS/Lambda | Batch/retry/DLQ, tránh infinite retry |
| CloudWatch | Log retention, metric/alarm volume |

Ước tính bằng AWS Pricing Calculator theo Region, volume, bytes scanned, job duration, worker type, request rate và retention.

## 14. Troubleshooting

| Symptom | Root cause candidates | Checks |
|---|---|---|
| Athena AccessDenied | IAM, bucket policy, KMS, Lake Formation | Query principal, result prefix, key policy, grants |
| Table not found | Sai catalog/database/Region | Workgroup, Catalog, SHOW DATABASES/TABLES |
| HIVE_BAD_DATA | CSV parser/schema mismatch | Header, delimiter, quote, encoding |
| Glue job fails startup | Role, script path, dependency, network | Job error, CloudWatch logs, role trust |
| Glue cannot read/write | S3/KMS permission | Source/target prefix và encryption |
| Crawler tạo table sai | Include path rộng, schema grouping | Target, table prefix, classifiers |
| Athena không thấy partitions | Metadata chưa update | Crawler / MSCK REPAIR TABLE khi phù hợp |
| Query scan lớn | CSV, SELECT *, partition chưa prune | Query details, format, filter |
| Lake Formation denies | Registration/grants/IAM interplay | Location role, grants, hybrid mode |
| SQS messages lặp | At-least-once/retry | Idempotency, visibility timeout, DLQ |

## 15. Cleanup checklist

- [ ] Stop Glue Job runs và crawler schedules.
- [ ] Drop demo tables/database nếu không giữ.
- [ ] Delete Glue Job/Crawler và dedicated IAM roles/policies.
- [ ] Delete S3 test outputs và versions sau khi xác minh bucket/prefix.
- [ ] Delete Athena Workgroup sau khi review query history/results.
- [ ] Remove Lake Formation registration/grants tạo riêng cho lab.
- [ ] Delete SQS/DLQ, Lambda, CloudWatch alarms nếu đã deploy.
- [ ] Kiểm tra incomplete multipart, log retention và Cost Explorer.

`DROP TABLE` thường chỉ xóa metadata; xác minh bucket/prefix trước khi delete objects. Không dùng production identifiers trong cleanup.

## 16. Knowledge check — 10 câu hỏi

1. Data Catalog khác S3 ở điểm nào?
2. Dùng Crawler khi nào, khi nào nên dùng explicit schema?
3. Glue Job role cần quyền gì để đọc Raw và ghi Prepared?
4. Lake Formation grant khác IAM policy ra sao?
5. Vì sao Athena query result location cần cấu hình riêng?
6. CSV khác Parquet về scan behavior như thế nào?
7. Partitioning giúp query nhanh hơn trong trường hợp nào?
8. Vì sao S3 event → SQS → Lambda cần idempotency?
9. Khi nào chọn Glue Workflow, Step Functions hoặc MWAA?
10. Chi phí UC02 gồm những thành phần nào ngoài Athena query?

## 17. Acceptance criteria

- [ ] Athena query đọc được raw CSV và trả kết quả đúng.
- [ ] Data Catalog database/table có đúng schema/location.
- [ ] Glue Crawler discovery đúng dataset.
- [ ] Glue ETL tạo Parquet output và quality checks pass.
- [ ] Athena query đọc được Parquet dataset.
- [ ] IAM/Lake Formation negative tests chứng minh boundary.
- [ ] Query scan, Glue runtime và cost drivers được ghi nhận.
- [ ] Cleanup hoàn tất và không còn billable resources do lab tạo.

## 18. Official references

- [AWS Glue User Guide](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html)
- [Glue ETL Jobs](https://docs.aws.amazon.com/glue/latest/dg/author-job.html)
- [Lake Formation Developer Guide](https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html)
- [Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
- [Athena pricing](https://aws.amazon.com/athena/pricing/)
- [S3 event notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)
- [SQS dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [AWS DataSync User Guide](https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html)
- [AWS Pricing Calculator](https://calculator.aws/)

**Last reviewed:** 2026-11-23. Xác minh Glue versions, Athena engine, Lake Formation mode, Region availability, quotas và pricing trước khi deploy.