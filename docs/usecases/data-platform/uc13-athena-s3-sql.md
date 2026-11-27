# UC13 — Amazon Athena: Truy vấn dữ liệu trực tiếp trên S3 bằng SQL

<small>DATA PLATFORM · SERVERLESS ANALYTICS · S3 + GLUE + ATHENA</small>

## 1. Mục tiêu

Thực hành tạo một data lake đơn giản trên Amazon S3 và dùng Amazon Athena để truy vấn file CSV bằng SQL mà không cần nạp dữ liệu vào database server.

Sau lab, bạn có thể:

- Tạo và tổ chức S3 bucket/prefix cho dữ liệu nguồn và query results.
- Cấu hình Athena Workgroup lần đầu.
- Tạo Glue Data Catalog database.
- Tạo table từ CSV theo hai cách: Glue Crawler hoặc SQL DDL.
- Chạy truy vấn SQL và hiểu mối quan hệ giữa S3, Glue Data Catalog và Athena.

> **Phân biệt quan trọng:** Athena không tự tạo table chỉ vì file đã nằm trên S3. File là data; Glue Data Catalog lưu metadata mô tả file (schema, location, format); Athena dùng metadata đó để đọc và query dữ liệu.

## 2. Kiến trúc và luồng hoạt động

~~~mermaid
flowchart LR
    U["Data Engineer"] -->|"Upload CSV"| S3[("Amazon S3<br/>raw/loan_demo/")]
    S3 -->|"Crawler đọc schema"| C["AWS Glue Crawler"]
    C -->|"Create / update metadata"| CAT[("Glue Data Catalog<br/>Database + Table")]
    CAT --> A["Amazon Athena"]
    U -->|"SQL query"| A
    A -->|"Read source objects"| S3
    A -->|"Write query output"| R[("S3<br/>athena-results/")]
~~~ 

**Vai trò từng thành phần**

| Thành phần | Vai trò |
|---|---|
| S3 bucket | Lưu CSV và kết quả query; không phải relational database. |
| S3 prefix | Phân vùng logic theo mục đích như `raw/`, `curated/`, `athena-results/`. |
| Glue Data Catalog | Lưu metadata database, table, column, data type, S3 location và partition. |
| Glue Crawler | Đọc dữ liệu để suy luận schema và tạo/cập nhật table metadata. |
| Athena | Serverless query engine thực thi SQL trên dữ liệu S3. |
| Workgroup | Quản lý query settings, result location, encryption, limits và tách biệt workload. |

## 3. Chuẩn bị S3 Bucket

### 3.1. Chọn bucket

Có thể dùng bucket learning đã tạo ở UC01 hoặc tạo bucket riêng. Trong ví dụ này giả sử:

- Bucket: `<bucket-name>`
- Region: `ap-southeast-1` (Singapore) — thay bằng Region thực tế của bucket và môi trường học.
- Dataset: `sample_loans.csv` — chỉ dùng dữ liệu synthetic.

Tên bucket S3 phải globally unique. Không dùng tên bucket ví dụ theo đúng nghĩa đen.

### 3.2. Tạo cấu trúc prefix

Tạo các prefix sau trong bucket:

```text
s3://<bucket-name>/
├── raw/
│   └── loan_demo/
│       └── sample_loans.csv
├── curated/
│   └── loan_demo_parquet/
└── athena-results/
```

- `raw/loan_demo/`: file CSV nguồn.
- `curated/`: dữ liệu đã chuẩn hóa/chuyển đổi về sau.
- `athena-results/`: kết quả query do Athena ghi ra.

**Lưu ý:** S3 là object storage theo bucket và object key; folder hiển thị trên Console thực chất là cách biểu diễn prefix, không phải thư mục vật lý.

### 3.3. Upload CSV

1. Mở **Amazon S3 → Buckets → bucket của bạn**.
2. Mở prefix `raw/loan_demo/` (tạo folder nếu chưa có).
3. Chọn **Upload → Add files**.
4. Chọn `sample_loans.csv`, sau đó Upload.
5. Kiểm tra object xuất hiện tại:

```text
s3://<bucket-name>/raw/loan_demo/sample_loans.csv
```

**Ảnh giao diện AWS Console:** thao tác upload file được minh họa trong [hướng dẫn chính thức của Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html). Các bước trên Console là **Buckets → chọn bucket → Upload → Add files → Upload**.

![AWS S3 Console – Upload objects](https://docs.aws.amazon.com/images/AmazonS3/latest/userguide/upload-objects-console.png)

*Ảnh tham khảo từ AWS Documentation. Giao diện có thể thay đổi theo phiên bản Console.*

### 3.4. Kiểm tra dữ liệu CSV

Ví dụ schema CSV dùng trong lab:

```csv
loan_id,product,principal_vnd,tenor_months,dpd,default_flag,snapshot_date
LN0001,MORTGAGE,1200000000,180,0,0,2026-09-30
LN0002,AUTO,450000000,60,15,0,2026-09-30
LN0003,CREDIT_CARD,25000000,12,95,1,2026-09-30
```

Khi upload file thật, hãy kiểm tra:
- Dòng header có đúng tên cột không.
- Delimiter là dấu phẩy hay dấu khác.
- Encoding có phù hợp không.
- Giá trị số/ngày có đúng format không.
- Không để lẫn nhiều file có schema khác nhau trong cùng prefix mà không có quy tắc rõ ràng.

## 4. Cấu hình Athena lần đầu

### 4.1. Mở Athena

1. AWS Console → tìm **Amazon Athena**.
2. Chọn đúng Region đang lưu S3 data và sử dụng Glue Catalog.
3. Mở **Query editor**.

### 4.2. Cấu hình Query result location

Lần đầu chạy query, Athena yêu cầu cấu hình nơi ghi kết quả:

1. Chọn **Edit settings** trong Query editor (hoặc Workgroup settings).
2. Tại **Query result location**, nhập:

```text
s3://<bucket-name>/athena-results/
```

3. Bật encryption theo chính sách môi trường (ví dụ SSE-S3 hoặc SSE-KMS).
4. Lưu cấu hình.

**Ảnh chụp AWS Console – Athena Query editor:** chọn **Edit settings** để khai báo S3 output location.

![Athena Query editor – Edit settings](https://docs.aws.amazon.com/images/athena/latest/ug/images/getting-started-choose-view-settings.png)

Nhập S3 path trong **Location of query result**, sau đó chọn **Save**:

![Athena Manage settings – Query result location](https://docs.aws.amazon.com/images/athena/latest/ug/images/getting-started-setting-results-location.png)

Sau khi lưu, quay lại tab **Editor**:

![Athena Query editor – Editor tab](https://docs.aws.amazon.com/images/athena/latest/ug/images/getting-started-choose-editor.png)

*Ảnh tham khảo từ AWS Documentation. Workgroup settings có thể override cấu hình phía Query editor.*

**Khuyến nghị:** Tạo Workgroup riêng tên `uc13-learning` thay vì dùng `primary` cho các lab dùng chung. Trong Workgroup có thể cấu hình:
- Query result location và encryption.
- Enforce workgroup configuration để người dùng không ghi đè thiết lập bắt buộc.
- Publish metrics và kiểm soát query.
- Data usage control / bytes-scanned cutoff để giới hạn chi phí.

Nếu Workgroup đã enforce cấu hình, setting của Workgroup sẽ được ưu tiên thay cho cấu hình phía client.

### 4.3. Chọn Data source và Catalog

Trong Query editor:
- Data source: `AwsDataCatalog` (Glue Data Catalog mặc định).
- Catalog: `AwsDataCatalog`.
- Database: chọn database sau khi tạo ở bước tiếp theo.

## 5. Tạo Database

Database của Athena là namespace metadata trong Glue Data Catalog; nó không tạo một database server hay copy dữ liệu.

Chạy câu lệnh:

```sql
CREATE DATABASE IF NOT EXISTS uc13_learning;
```

Ảnh minh họa Query editor và câu lệnh tạo Database trong [AWS Athena getting started guide](https://docs.aws.amazon.com/athena/latest/ug/step-1-create-a-database.html):

![Athena Query editor – nhập CREATE DATABASE](https://docs.aws.amazon.com/images/athena/latest/ug/images/getting-started-collapse-nav-pane.png)

Sau đó chọn database `uc13_learning` ở panel bên trái hoặc dùng:

```sql
SHOW DATABASES;
```

## 6. Tạo Table từ file CSV

Có hai cách phổ biến. Cả hai đều tạo metadata table trong Glue Data Catalog; dữ liệu CSV vẫn nằm nguyên trên S3.

### Cách A — Sử dụng Glue Crawler (dễ bắt đầu)

Glue Crawler tự đọc một hoặc nhiều data source để suy luận schema và tạo/cập nhật table trong Data Catalog.

#### A1. Mở AWS Glue

1. AWS Console → **AWS Glue**.
2. Vào **Data Catalog → Crawlers**.
3. Chọn **Create crawler**.

#### A2. Đặt tên Crawler

![AWS Glue Console – Crawlers page và nút Create crawler](https://docs.aws.amazon.com/images/glue/latest/dg/images/crawlers-create_crawler.png)

*Ảnh tham khảo từ AWS Glue Documentation.*

- Crawler name: `uc13-loan-demo-crawler`.
- Description: `Discover schema for UC13 Athena CSV lab`.

#### A3. Chọn Data source

1. Chọn **Add a data source**.
2. Data source: **S3**.
3. S3 path:

```text
s3://<bucket-name>/raw/loan_demo/
```

4. Nếu có lựa chọn **Subsequent crawler runs**, chọn hành vi phù hợp với việc cập nhật schema.
5. Không trỏ Crawler vào toàn bộ bucket nếu chỉ cần khám phá một dataset.

#### A4. Cấu hình IAM role

Chọn IAM role dành cho Glue Crawler, ví dụ `AWSGlueServiceRole-UC13`.

Role cần quyền tối thiểu phù hợp để:
- Đọc/list đúng S3 source prefix.
- Ghi metadata vào Glue Data Catalog.
- Ghi CloudWatch Logs.
- Decrypt object bằng KMS nếu source dùng SSE-KMS.

Không dùng AdministratorAccess chỉ để chạy lab.

#### A5. Chọn Database

- Chọn database có sẵn: `uc13_learning`.
- Hoặc tạo database mới nếu chưa có.
- Table name prefix có thể để trống hoặc đặt `src_`.

#### A6. Review và Run

1. Review cấu hình.
2. Chọn **Create crawler**.
3. Mở Crawler và bấm **Run**.
4. Chờ trạng thái chuyển sang **Ready** và xem Last run status.
5. Mở **Data Catalog → Tables**, chọn database `uc13_learning`.
6. Kiểm tra table được tạo, column và S3 location.

**Khi nào dùng Crawler?**

- Dataset mới, chưa rõ schema.
- Muốn bắt đầu nhanh với CSV/JSON/Parquet.
- Có nhiều folder hoặc dataset cần discover metadata.
- Chấp nhận kiểm tra lại schema mà Crawler suy luận trước khi dùng production.

**Cần chú ý:** Crawler có thể tạo schema chưa đúng kỳ vọng khi CSV không đồng nhất, header bất thường, nhiều file khác cấu trúc hoặc partition layout chưa chuẩn. Luôn kiểm tra column/type và table location.

### Cách B — Tạo Table bằng SQL DDL

Cách này phù hợp khi đã biết schema, cần kiểm soát data type, SerDe, header và location chính xác.

Trong Athena Query editor, chọn database `uc13_learning`, sau đó chạy. AWS minh họa thao tác tạo query tab và nhập DDL trong [hướng dẫn Create a table](https://docs.aws.amazon.com/athena/latest/ug/step-2-create-a-table.html):

![Athena Query editor – tạo query tab mới](https://docs.aws.amazon.com/images/athena/latest/ug/images/getting-started-new-query-tab.png)



```sql
CREATE EXTERNAL TABLE IF NOT EXISTS uc13_learning.loan_demo_csv (
    loan_id        STRING,
    product        STRING,
    principal_vnd  BIGINT,
    tenor_months   INT,
    dpd            INT,
    default_flag   INT,
    snapshot_date  STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'escapeChar' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://<bucket-name>/raw/loan_demo/'
TBLPROPERTIES ('skip.header.line.count' = '1');
```

Thay `<bucket-name>` bằng bucket thật. Prefix trong `LOCATION` phải trỏ tới nơi chứa CSV.

Kiểm tra metadata:

```sql
SHOW TABLES IN uc13_learning;

DESCRIBE uc13_learning.loan_demo_csv;

SHOW CREATE TABLE uc13_learning.loan_demo_csv;
```

**Giải thích các thành phần DDL**

| Thành phần | Ý nghĩa |
|---|---|
| `CREATE EXTERNAL TABLE` | Tạo metadata table trỏ đến dữ liệu bên ngoài, không copy CSV. |
| Column definitions | Khai báo tên cột và data type. |
| `OpenCSVSerde` | Đọc CSV, xử lý delimiter/quote/escape. |
| `STORED AS TEXTFILE` | Dữ liệu được lưu dưới dạng text. |
| `LOCATION` | S3 prefix chứa object nguồn. |
| `skip.header.line.count` | Bỏ dòng header khi đọc CSV. |

**Lưu ý về CSV:** `OpenCSVSerde` có các giới hạn về kiểu dữ liệu và định dạng ngày; trong lab khai báo ngày là STRING trước, sau đó chuyển kiểu bằng SQL. Nếu CSV có nested JSON, multiline fields hoặc format đặc thù, cần chọn SerDe/format phù hợp và test với sample.

### So sánh hai cách

| Tiêu chí | Glue Crawler | SQL DDL |
|---|---|---|
| Tốc độ bắt đầu | Nhanh, ít phải viết SQL | Cần khai báo schema |
| Kiểm soát schema | Crawler suy luận, cần review | Chủ động chỉ định |
| Phù hợp | Khám phá dữ liệu, onboarding | Schema ổn định, repeatable deployment |
| Rủi ro | Suy luận sai hoặc thay đổi schema | Khai báo sai type/location |
| Tự động hóa | Schedule/event crawler | Migration script / IaC / CI |

> Không nên chạy cả hai cách lên cùng một table name. Nếu muốn so sánh, hãy dùng hai table name khác nhau hoặc xóa metadata lab trước khi tạo lại.

## 7. Truy vấn dữ liệu bằng SQL

Sau khi table xuất hiện trong Catalog, Athena có thể chạy SQL trực tiếp trên CSV trong S3.

### 7.1. Xem dữ liệu

```sql
SELECT *
FROM uc13_learning.loan_demo_csv
LIMIT 10;
```

### 7.2. Đếm số khoản vay

```sql
SELECT COUNT(*) AS account_count
FROM uc13_learning.loan_demo_csv;
```

### 7.3. Tổng dư nợ theo sản phẩm

```sql
SELECT
    product,
    COUNT(*) AS account_count,
    SUM(principal_vnd) AS total_principal_vnd,
    AVG(dpd) AS average_dpd
FROM uc13_learning.loan_demo_csv
GROUP BY product
ORDER BY total_principal_vnd DESC;
```

### 7.4. Phân tích nợ quá hạn

```sql
SELECT
    CASE
        WHEN dpd = 0 THEN 'CURRENT'
        WHEN dpd BETWEEN 1 AND 30 THEN 'DPD_01_30'
        WHEN dpd BETWEEN 31 AND 90 THEN 'DPD_31_90'
        ELSE 'DPD_OVER_90'
    END AS dpd_bucket,
    COUNT(*) AS account_count,
    SUM(principal_vnd) AS exposure_vnd
FROM uc13_learning.loan_demo_csv
GROUP BY 1
ORDER BY 1;
```

### 7.5. Chuyển STRING thành DATE

```sql
SELECT
    loan_id,
    TRY_CAST(snapshot_date AS DATE) AS snapshot_dt
FROM uc13_learning.loan_demo_csv;
```

## 8. Phân quyền IAM — nguyên tắc tối thiểu

Một người chạy Athena thường cần quyền trên nhiều lớp:

1. Athena: thao tác query và Workgroup được phép.
2. Glue Data Catalog: đọc database/table metadata; quyền create/update nếu người dùng trực tiếp tạo table.
3. S3 source: `ListBucket` giới hạn theo prefix và `GetObject` trên object nguồn.
4. S3 query results: `GetBucketLocation`, `ListBucket` khi cần và `PutObject`; quyền đọc/xóa output chỉ cấp nếu workflow yêu cầu.
5. KMS: `Decrypt` cho source và `Encrypt`/`GenerateDataKey` cho output tùy cấu hình key.
6. Glue Crawler execution role riêng: quyền đọc source và cập nhật Catalog.

**Thiết kế production:** tách role của Data Engineer/Crawler và Analyst; giới hạn bucket/prefix, database/table, Workgroup; bật encryption; dùng Lake Formation khi cần quản trị quyền ở mức database/table/column/row. Không đưa access key vào source code.

## 9. Troubleshooting

| Hiện tượng | Nguyên nhân thường gặp | Cách kiểm tra |
|---|---|---|
| Query editor báo chưa có output location | Workgroup chưa cấu hình result location | Kiểm tra Workgroup settings và S3 output prefix |
| `AccessDenied` | Thiếu quyền Athena, Glue, S3 hoặc KMS | Kiểm tra IAM policy, bucket policy, key policy, Lake Formation |
| Table không xuất hiện | Crawler chưa chạy, chọn nhầm database/Region | Xem Crawler run, Catalog và Athena Region |
| Query trả 0 rows | Sai S3 LOCATION hoặc prefix không có file phù hợp | Đối chiếu object key và table location |
| `HIVE_BAD_DATA` / lỗi parse | CSV delimiter, quote hoặc type không đúng | Mở sample CSV, kiểm tra DDL/SerDe |
| Header bị xem là record | Chưa cấu hình skip header | Kiểm tra `skip.header.line.count` |
| Cột bị lệch | File CSV có quoted delimiter hoặc schema không đồng nhất | Kiểm tra CSV parser/SerDe |
| Query scan quá lớn | CSV text, select nhiều cột, không partition | Chuyển Parquet, chọn cột và lọc partition |

## 10. Chi phí và tối ưu

- Athena tính phí query theo lượng dữ liệu scan theo pricing model của Region; kiểm tra pricing hiện hành trước khi triển khai.
- Dữ liệu CSV thường scan nhiều hơn định dạng columnar.
- Chỉ chọn các cột cần thiết, tránh `SELECT *` trên dataset lớn.
- Chuyển dữ liệu sang Parquet hoặc ORC để giảm scan.
- Partition theo cột filter thường dùng, ví dụ `snapshot_date` hoặc `process_date`.
- Tránh small files và partition quá nhỏ.
- Workgroup có thể đặt per-query data usage control để hạn chế chi phí.
- S3 query results, storage, request và KMS có thể phát sinh chi phí riêng.

## 11. Cleanup

1. Xóa table metadata lab nếu không dùng nữa:

```sql
DROP TABLE IF EXISTS uc13_learning.loan_demo_csv;
DROP DATABASE IF EXISTS uc13_learning;
```

2. Xóa Glue Crawler `uc13-loan-demo-crawler` nếu đã tạo.
3. Xóa object trong đúng prefix lab: `raw/loan_demo/` và `athena-results/`.
4. Xóa Workgroup `uc13-learning` nếu không còn nhu cầu.
5. Nếu bucket bật versioning, kiểm tra và xóa các object versions/delete markers phù hợp.
6. Xác nhận không xóa nhầm dữ liệu dùng chung.

> `DROP TABLE` chỉ xóa metadata table trong Catalog, không đảm bảo xóa các object CSV trên S3.

## 12. Checklist hoàn thành

- [ ] CSV đã upload đúng S3 prefix.
- [ ] Athena Workgroup có query result location và encryption.
- [ ] Database `uc13_learning` đã tạo.
- [ ] Tạo được table bằng Glue Crawler **hoặc** SQL DDL.
- [ ] `DESCRIBE` hiển thị schema đúng.
- [ ] Query `SELECT`, `COUNT`, `GROUP BY` chạy thành công.
- [ ] Đã kiểm tra bytes scanned và query output.
- [ ] Đã hiểu quyền IAM trên Athena, Glue, S3 và KMS.
- [ ] Đã cleanup tài nguyên lab.

## 13. Tài liệu tham khảo chính thức

- [What is Amazon Athena?](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
- [Getting started with Athena](https://docs.aws.amazon.com/athena/latest/ug/getting-started.html)
- [Creating tables in Athena](https://docs.aws.amazon.com/athena/latest/ug/creating-tables.html)
- [Using AWS Glue crawlers](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html)
- [Athena Workgroups](https://docs.aws.amazon.com/athena/latest/ug/workgroups-create-update-delete.html)
- [Athena pricing](https://aws.amazon.com/athena/pricing/)
