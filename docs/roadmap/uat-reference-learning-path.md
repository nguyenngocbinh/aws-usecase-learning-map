# Lộ trình học AWS từ kiến trúc Data Platform thực tế

Lộ trình biến kiến trúc tham chiếu trong tài liệu AWS UAT v1.6 thành chuỗi bài thực hành độc lập. Thứ tự đi từ network/identity/data foundation đến analytics, CI/CD, operations và ML.

## Phase 1 — Foundation

| Bài | Học gì | Kết quả |
|---|---|---|
| AWS Fundamentals | Account, Region, IAM, STS, CLI, billing | Learning account an toàn |
| UC01 | S3, upload, versioning, encryption | Upload synthetic file |
| IAM guide | Role, trust policy, policy evaluation | Debug AccessDenied |
| Network reference | VPC, route, DNS, VPC Endpoint | Đọc central endpoint topology |

## Phase 2 — Data Platform

| Bài | Học gì | Kết quả |
|---|---|---|
| UC02 | S3 zones, Glue Catalog, Crawler, ETL | Raw → Prepared |
| Athena | Workgroup, SQL, CTAS, Parquet, partitions | Query Curated |
| Lake Formation | Data location, database/table grants | Producer/analyst boundary |
| UC03 | DataSync/DMS, source/destination, validation | Migration rehearsal |

## Phase 3 — Infrastructure Automation

| Bài | Học gì | Kết quả |
|---|---|---|
| Terraform basics | Modules, variables, state, workspace | Reproducible IaC |
| Remote state | S3 backend, versioning, locking | Shared state governance |
| UC07 | GitHub OIDC | Workflow assume AWS role |
| UC08 | GitLab OIDC / cross-account AssumeRole | GitLab deployment |
| UC09 | Validate → plan → scan → approval → apply | Controlled deployment |

## Phase 4 — Operations

| Bài | Học gì | Kết quả |
|---|---|---|
| UC10 | EventBridge, Step Functions, MWAA | Scheduled workflows |
| UC11 | CloudWatch, CloudTrail, SNS, SQS DLQ | Alarms và incident runbook |
| UC12 | KMS, backup, restore, DR | Recovery exercise |

## Phase 5 — Machine Learning

| Bài | Học gì | Kết quả |
|---|---|---|
| UC04 | SageMaker training, artifacts, registry | Versioned model |
| UC05 | Real-time inference/API | Authenticated model endpoint |
| UC06 | Batch scoring/monitoring | Reproducible batch output |

## Mỗi service cần 10 WH

1. **What:** service là gì?
2. **Why:** tại sao cần?
3. **When:** trường hợp nào nên/không nên dùng?
4. **Where:** Region, network, placement và integration?
5. **Who:** actor/role/persona nào vận hành?
6. **Which:** chọn mode/tier/config nào?
7. **How:** tạo và vận hành thế nào?
8. **How much:** pricing dimensions và cost drivers?
9. **What if:** failure modes, limits và recovery?
10. **How compared:** alternatives và trade-offs?

## Definition of done mỗi lab

- Scenario và learning objectives.
- Architecture/data flow, prerequisites và account boundary.
- Console steps, CLI/SDK/IaC examples phù hợp.
- Expected output và validation.
- Security/least privilege.
- Cost model theo usage.
- Troubleshooting.
- Cleanup/teardown.
- Knowledge check.
- Status: Draft, Content complete, Code checked, AWS lab verified.