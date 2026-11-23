# UC02 — S3 Data Lake và Athena SQL Lab

Tài liệu hướng dẫn thực hành bước đầu để lưu dữ liệu trên Amazon S3, đăng ký metadata trong AWS Glue Data Catalog và truy vấn bằng Amazon Athena.

## Phạm vi

- Tái sử dụng dữ liệu synthetic sample_loans.csv từ UC01.
- S3 prefixes: landing/loan_demo/, curated/loan_demo_parquet/, athena-results/.
- Tạo Athena Workgroup riêng cho learning lab.
- Tạo Glue Data Catalog database và external table cho CSV.
- Chạy SQL validation và aggregation.
- Chuyển CSV sang Parquet bằng Athena CTAS.
- Kiểm tra bytes scanned, security permissions và cleanup.

## Prerequisites

- Hoàn thành UC01 hoặc upload file usecases/UC01/data/sample_loans.csv lên S3.
- AWS CLI v2 đã đăng nhập bằng SSO/role.
- Bucket riêng cho learning account.
- Athena, Glue Catalog và S3 permissions phù hợp.
- Chọn cùng Region cho S3, Glue Catalog và Athena.

## Run order

1. Đọc [Amazon S3 service guide](../../docs/aws-services/s3.md).
2. Đọc [Amazon Athena service guide](../../docs/aws-services/athena.md).
3. Tạo Workgroup uc02-learning và cấu hình query result location.
4. Thay `<bucket-name>` trong file SQL bằng tên bucket thực tế.
5. Chạy sql/01_athena_create_database_and_csv_table.sql.
6. Chạy sql/02_athena_ctas_parquet.sql.
7. So sánh query details/bytes scanned giữa CSV và Parquet.
8. Hoàn thành cleanup trong hướng dẫn Athena.

## SQL assets

- sql/01_athena_create_database_and_csv_table.sql: Glue Catalog database, CSV external table và validation.
- sql/02_athena_ctas_parquet.sql: CTAS chuyển đổi CSV sang Parquet.

## Security và cost

- Chỉ dùng dữ liệu synthetic; không upload dữ liệu khách hàng hoặc dữ liệu nội bộ.
- Không commit credentials, access keys hoặc Terraform state.
- Không cấp s3:* trên toàn account chỉ để làm lab.
- Query results cũng được lưu trên S3 và có thể phát sinh storage/request cost.
- Athena query cost phụ thuộc lượng dữ liệu scan; kiểm tra bytes scanned sau mỗi query.
- CTAS target prefix phải rỗng và chỉ dùng cho lab. Không cleanup trên prefix dùng chung.

## Trạng thái

Đây là lab hướng dẫn và SQL assets. Chưa có xác nhận đã deploy hoặc chạy trên AWS account thật. Cần thực hiện trên learning account để xác minh IAM permissions, Region, pricing và kết quả thực tế.
