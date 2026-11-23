# Project Todos

This page mirrors the detailed implementation plan in [PROJECT_TODOS.md](https://github.com/nguyenngocbinh/aws-usecase-learning-map/blob/main/PROJECT_TODOS.md).

## Milestone overview

- [x] M0 — Repository foundation, language conventions and project structure.
- [x] M1 — Documentation portal, navigation and Mermaid support.
- [ ] M2 — AWS service knowledge base: 10 WH questions + alternatives for every service.
- [ ] M3 — All 12 use cases and verified hands-on labs.
- [ ] M4 — Python, SQL, YAML, Terraform, tests and cleanup.
- [ ] M5 — GitHub Actions, Pages, quality and security checks.
- [ ] M6 — End-to-end Retail Credit Risk reference project.

## Các tài liệu vừa bổ sung

| Topic | Nội dung | Trạng thái |
|---|---|---|
| AWS UAT reference | Multi-account, Centralized VPC Endpoints, DataSync, Glue, Lake Formation, MWAA, SageMaker, CI/CD | Documentation added; not deployed |
| UC02 | S3 Data Lake, Glue Crawler/ETL, Lake Formation, Athena CTAS/Parquet, cost, troubleshooting, cleanup | Expanded; AWS execution not verified |
| UC09 | Terraform pipeline, GitHub OIDC, GitLab CI, remote state, approval, runner operations | Expanded; AWS execution not verified |
| S3 / Athena | 10 WH, alternatives, architecture, lab and cost | Expanded |
| UAT mapping | Chapter-to-use-case traceability and sanitization rules | Added |
| Guided learning path | Foundation → Data → DevOps → Operations → ML | Added |

## Các việc còn lại

- [ ] Bổ sung đầy đủ 10 WH và comparison matrix cho mọi AWS service được dùng trong 12 use cases.
- [ ] Hoàn thiện UC03 — DMS/SCT, SQL Server migration rehearsal, validation và cutover.
- [ ] Hoàn thiện UC04–UC06 — SageMaker training, model API, batch scoring.
- [ ] Hoàn thiện UC07–UC08 — end-to-end GitHub/GitLab federation labs.
- [ ] Hoàn thiện UC10–UC12 — orchestration, monitoring, security, backup và DR.
- [ ] Bổ sung Terraform modules và automated tests cho S3, Glue, Athena, IAM.
- [ ] Tạo synthetic dataset, expected outputs và executable test scripts.
- [ ] Chạy AWS labs trong isolated learning account; capture redacted screenshots.
- [ ] Kiểm tra cost/cleanup và ghi lại lab run evidence.
- [ ] Chạy `mkdocs build --strict`, link checks và code validation.
- [ ] Kiểm tra GitHub Pages deployment sau khi merge.

## Quality gates

- [ ] Không có credentials, real account IDs, internal hostnames hoặc customer data.
- [ ] Mọi architecture diagram có editable Mermaid/Draw.io source.
- [ ] External AWS claims/pricing links được kiểm tra theo ngày.
- [ ] Mọi lab có security, expected output, troubleshooting, cost và cleanup.
- [ ] Không gắn “Lab verified” khi chưa có evidence chạy trên AWS account.

## Definition of done

Tiếng Việt cho phần giải thích; English cho code, command, AWS resource/service names và technical terms. Mỗi service page phải có đủ 10 WH và alternatives. Mỗi use case phải có architecture, prerequisites, hands-on steps, expected output, validation, security, cost, troubleshooting, cleanup và knowledge check.