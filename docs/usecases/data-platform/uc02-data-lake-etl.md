# UC02 — Xây dựng Data Lake và ETL

> **UC02 · DATA PLATFORM · IN PROGRESS**

## 1. Business scenario
Xây data lake nhiều zone và ETL có catalog, query, orchestration, kiểm soát quyền và chi phí.

## 2. Learning objectives
- Giải thích bài toán, dữ liệu đầu vào/đầu ra và yêu cầu vận hành.
- Đọc và thiết kế được kiến trúc AWS, data flow và trust boundaries.
- Chọn dịch vụ theo workload, security, availability, operations và cost.
- Triển khai bằng Console, CLI/SDK và IaC khi phù hợp.
- Kiểm thử, xử lý lỗi, quan sát hệ thống và dọn dẹp tài nguyên.

## 3. Reference architecture
```mermaid
flowchart LR
  A["Source / Trigger"] --> B["AWS ingestion / integration"]
  B --> C["S3 / Database"]
  C --> D["Processing / Workload"]
  D --> E["Output / Validation"]
  D -. telemetry .-> F["CloudWatch / Audit"]
```
**Logical flow:** Source → S3 Raw → Glue ETL → S3 Curated → Catalog → Athena.

> Sơ đồ này là bản khái niệm. Bản hoàn thiện cần thể hiện VPC/subnet, endpoints, encryption, IAM trust, network path, error handling và service-specific boundaries theo lab thực tế.

## 4. AWS service selection
- **Amazon S3** — lưu trữ Raw/Curated Zone, object layout, security, lifecycle và cost. Xem [S3 service guide](../../aws-services/s3.md).
- **AWS Glue Data Catalog** — lưu metadata database/table/schema/location; lab hiện tại tạo Catalog database/table qua Athena DDL.
- **Amazon Athena** — query SQL trực tiếp trên S3, Workgroup, CSV external table và CTAS Parquet. Xem [Athena service guide](../../aws-services/athena.md).
- **AWS Glue ETL, Lambda, Step Functions và Lake Formation** — sẽ triển khai ở các lab mở rộng tiếp theo.
- **Lambda** — đánh giá vai trò và cấu hình phù hợp trong lab.
- **Step Functions** — đánh giá vai trò và cấu hình phù hợp trong lab.
- **Lake Formation** — đánh giá vai trò và cấu hình phù hợp trong lab.

### 10 WH questions — áp dụng cho từng service
| WH | Câu hỏi bắt buộc |
|---|---|
| What | Dịch vụ là gì, giải quyết capability nào? |
| Why | Vì sao chọn dịch vụ cho scenario này? |
| When | Trường hợp nào nên/không nên dùng? |
| Where | Region, AZ, network placement và availability ra sao? |
| Who | Ai vận hành, IAM principal nào cần quyền? |
| Which | Nên chọn mode, tier hoặc configuration nào? |
| How | Triển khai bằng Console, CLI, SDK và IaC thế nào? |
| How much | Pricing dimensions và cost drivers là gì? |
| What if | Failure modes, limits, recovery và troubleshooting? |
| How compared | So với alternative nào, trade-off ra sao? |

**Status:** S3 và Athena đã có service guide riêng với 10 WH, alternatives, pricing drivers, security, troubleshooting và official references. Các service còn lại sẽ được hoàn thiện theo từng lab.

## 5. Alternatives and decision matrix
| Choice | When to consider | Trade-offs to validate |
|---|---|---|
| AWS managed service | Giảm vận hành hạ tầng | Feature fit, quotas, limits, pricing |
| Self-managed on EC2/container | Cần OS/runtime/customization | Patching, HA, scaling, backup, operations |
| Alternative AWS service | Workload khác về latency/scale/governance | Fit, migration effort, integration, cost |

## 6. Prerequisites
- AWS learning account riêng, MFA và budget/billing alert.
- AWS CLI v2 và identity dùng temporary credentials.
- Git và Python/Docker/Terraform nếu lab cần.
- Synthetic dataset; không dùng dữ liệu khách hàng hoặc thông tin nội bộ.
- Xác nhận Region, quota, service availability và IAM permissions.

## 7. Hands-on labs

| Lab | Nội dung | Trạng thái |
|---|---|---|
| Lab 01 | Chuẩn bị learning account, IAM identity, Region và S3 bucket | Có hướng dẫn trong UC01 |
| Lab 02 | Upload synthetic CSV lên S3 Raw Zone | Có hướng dẫn và code trong UC01 |
| Lab 03 | Tạo Athena Workgroup và Glue Data Catalog database/table | Có hướng dẫn SQL |
| Lab 04 | Query, aggregation và Data Quality checks bằng Athena SQL | Có SQL examples |
| Lab 05 | Dùng CTAS chuyển CSV sang Parquet; kiểm tra bytes scanned, security và cleanup | Có SQL examples; cần chạy xác minh trên AWS account |

### Tài liệu và mã nguồn

- [Amazon S3 service guide](../../aws-services/s3.md)
- [Amazon Athena service guide](../../aws-services/athena.md)
- [UC02 README và run order](../../../usecases/UC02/README.md)
- [SQL 01 — Create database và CSV external table](https://github.com/nguyenngocbinh/aws-usecase-learning-map/blob/feature/s3-athena-hands-on/usecases/UC02/sql/01_athena_create_database_and_csv_table.sql)
- [SQL 02 — CTAS Parquet](https://github.com/nguyenngocbinh/aws-usecase-learning-map/blob/feature/s3-athena-hands-on/usecases/UC02/sql/02_athena_ctas_parquet.sql)

**Giới hạn xác minh:** tài liệu và SQL assets đã được chuẩn bị trong repository; chưa có xác nhận đã deploy hoặc chạy trên AWS account thật. Chưa có ảnh chụp màn hình Console thực tế.

## 8. Code and infrastructure
Mã nguồn thực hành được tổ chức trong `usecases/UC02/`:
- `src/`: runnable Python/SQL/shell source.
- `config/`: safe examples và `.env.example` (không lưu secrets thật).
- `infrastructure/terraform/`: infrastructure có thể tái triển khai.
- `tests/`: unit, integration và data validation tests.
- `diagrams/`: Mermaid/Draw.io source và exported images.

## 9. Security, cost and cleanup
- Least-privilege IAM; không hard-code credentials.
- Encryption và secrets management phù hợp với phân loại dữ liệu.
- Chỉ dùng synthetic data; ghi rõ retention và access.
- Ghi Region, assumptions, pricing dimensions và ngày kiểm tra.
- Có teardown cụ thể và xác minh tài nguyên đã được xóa.
- Không chạy destructive commands ngoài learning environment riêng.

## 10. Troubleshooting and operations
Tạo bảng symptom → likely cause → diagnostic → remediation. Bổ sung CloudWatch logs/metrics, audit trail, retry behavior, alert routing và recovery checks khi phù hợp.

## 11. Knowledge check
- [ ] Trả lời đủ 10 WH cho từng AWS service.
- [ ] So sánh service chính với ít nhất hai alternatives khả thi khi phù hợp.
- [ ] Giải thích architecture, data flow và security boundaries.
- [ ] Reproduce lab từ môi trường sạch.
- [ ] Chẩn đoán ít nhất một failure được chủ động tạo ra.
- [ ] Ước tính chi phí và hoàn thành teardown.

## 12. Official references
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS Pricing Calculator](https://calculator.aws/)

Bổ sung service-specific official docs, quotas/limits, pricing links và ngày kiểm tra khi triển khai lab.