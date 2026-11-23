# Mapping tài liệu AWS UAT v1.6 vào AWS Use Case Learning Map

Nguồn: *Tài liệu hướng dẫn triển khai hệ thống trên AWS (UAT), version 1.6*, cập nhật 11-Feb-2026. Mapping giúp chuyển tài liệu triển khai thành chương trình học; không xác nhận cấu hình UAT có thể copy sang account khác.

## 1. Mapping theo chương

| Vị trí | Nội dung nguồn | Use case / lesson |
|---|---|---|
| Trang 5–12 | Tools, multi-account, DataSync Agent, VPC Endpoints, Runner network, S3 Terraform state | UC01 Upload; UC03 Migration; UAT architecture |
| Trang 13–20 | Deploy permissions, CI/CD assume roles, IAM trust policy, ExternalId | UC07 GitHub → AWS; UC08 GitLab → AWS; UC09 CI/CD; IAM guide |
| Trang 21–33 | Terraform layout, S3, Glue Catalog/Job/Crawler, Lake Formation, DataSync, SQS/Lambda, API Gateway, CloudWatch, SNS, Backup | UC02 Data Lake & ETL; UC10 Scheduling; UC11 Monitoring; UC12 Backup & DR |
| Trang 34–45 | Shared Services ECS GitLab Runner, ECR images, SSM, IAM roles, CloudWatch, Security Groups | UC08 GitLab → AWS; UC09 CI/CD |
| Trang 46–56 | Retail Banking Terraform, MWAA, SageMaker Domain/User Profiles, KMS, ECR, SNS | UC04 Model Training; UC05 Model API; UC06 Batch Scoring; UC10 Scheduling; UC11 Monitoring |
| Trang 57–70 | GitLab CI/CD files, dynamic pipeline, variables, plan/compliance/deploy, approval | UC08 GitLab → AWS; UC09 CI/CD |
| Trang 71 trở đi | Manual Terraform deployment và pipeline execution | UC09 CI/CD và infrastructure labs |

## 2. Thành phần triển khai được rút ra

- Multi-account responsibility boundaries.
- Centralized network connectivity và VPC Endpoint governance.
- DataSync từ On-Premises NFS/SMB đến S3.
- Data Lake zones: Raw, Prepared, Curated.
- Glue Catalog, Crawler và ETL.
- Lake Formation data permissions.
- S3 → SQS → Lambda → Glue event-driven pattern.
- Athena query-serving API qua API Gateway/Lambda.
- S3 Terraform remote state tại Shared Services.
- ECS/Fargate GitLab Runner manager và worker.
- ECR runner images; SSM Parameter Store cho registration token.
- Cross-account deployment roles và ExternalId.
- MWAA orchestration, SageMaker Domain/User Profiles/Pipelines.
- CloudWatch Logs/Alarms, SNS notifications và S3 backup resources.

## 3. Security and public repository sanitization

Không lưu trong public learning repository:
- Real AWS account IDs, ARNs, role names gắn tổ chức, VPC/subnet IDs và CIDRs.
- Internal GitLab URLs, internal hostnames, private DNS records và IP addresses.
- Registration token, credentials, secret values, access keys và session tokens.
- Email cá nhân hoặc thông tin liên hệ không phục vụ bài học.
- Customer data, loan/account IDs hoặc production/UAT datasets.

Policy examples dùng placeholders; policy cho lab cần scope hẹp và review trước deploy.

## 4. Nội dung nguồn chưa xác nhận

Tài liệu UAT không nên được hiểu là cung cấp đầy đủ:
- Toàn bộ Low Level Design cho Raw–Prepared–Curated.
- Data transformation business rules/schema contract cho mọi dataset.
- Production approval matrix/SoD đầy đủ.
- RPO/RTO và disaster recovery exercise evidence.
- Cost baseline/workload sizing cho mọi service.
- Hướng dẫn mọi application use-case pipeline.
- GitHub OIDC implementation; tài liệu tập trung GitLab CI/CD.

Các phần này cần design owners hoặc AWS official documentation; phải đánh dấu assumptions rõ ràng.

## 5. Recommended learning sequence

1. UC01: S3 upload, IAM và encryption.
2. UC02: S3 Data Lake, Glue, Lake Formation và Athena.
3. UC03: DataSync/DMS và database migration.
4. UC07/08/09: GitHub/GitLab federation và Terraform CI/CD.
5. UC10/11: orchestration, logs, alarms, DLQ.
6. UC04/05/06: SageMaker training, deploy, batch scoring.
7. UC12: security, backup và DR.

## 6. Reference-to-lab rule

Mỗi bài cần ghi:
- **Source-derived:** nội dung được tài liệu UAT mô tả.
- **Learning adaptation:** phần thay đổi để chạy trong learning account.
- **External verification:** behavior/pricing/API kiểm tra từ AWS official docs.
- **Not verified:** nội dung chưa thực hành trên AWS account.

Không gắn “Lab verified” nếu mới viết tài liệu hoặc chạy syntax validation.