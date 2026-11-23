# Kiến trúc tham chiếu AWS Cloud Data Platform — từ tài liệu UAT v1.6

> Nội dung tổng hợp từ tài liệu AWS UAT v1.6 (cập nhật 11-Feb-2026), đã khái quát hóa để học tập. Không phải kiến trúc chuẩn cho mọi tổ chức. Không lưu account IDs, ARNs, internal URLs, registration tokens, email, CIDR, secrets hoặc tên resource nội bộ.

## 1. Mục tiêu

Tài liệu UAT mô tả triển khai Data Platform trên AWS theo mô hình multi-account, dùng Terraform quản lý infrastructure và GitLab CI/CD tự động hóa deployment.

- **Shared Services:** GitLab Runner infrastructure, ECR, SSM Parameter Store, Terraform remote state.
- **Data Platform:** S3 Data Lake, Glue Data Catalog/Jobs/Crawlers, Lake Formation, DataSync và API serving.
- **Retail Banking / Analytics:** MWAA, SageMaker, S3 và IAM roles phục vụ CI/CD/ML.
- **Network account:** Centralized VPC Endpoints, Private Hosted Zone và routing cho member accounts.

## 2. Logical architecture

~~~mermaid
flowchart TB
  GIT["GitLab On-Prem / Source Repository"]
  subgraph SHARED["Shared Services Account"]
    RM["ECS GitLab Runner Manager"]
    RW["ECS/Fargate Runner Workers"]
    ECR["Amazon ECR"]
    SSM["SSM Parameter Store"]
    STATE[("S3 Terraform State")]
    LOG["CloudWatch Logs"]
    RM --> RW
    RW --> ECR
    RW --> STATE
    RM --> SSM
    RM --> LOG
    RW --> LOG
  end
  subgraph NETWORK["Network Account"]
    VPCE["Central VPC Endpoints"]
    PHZ["Route 53 Private Hosted Zones"]
  end
  subgraph DP["Data Platform Account"]
    S3[("S3 Data Lake: Raw / Prepared / Curated")]
    GLUE["Glue Catalog / ETL / Crawler"]
    LF["Lake Formation"]
    DS["DataSync Agent / Locations / Tasks"]
    API["API Gateway + Lambda"]
    Q["SQS"]
    S3 --> GLUE
    LF -. authorization .-> GLUE
    DS --> S3
    S3 --> Q
    Q --> API
  end
  subgraph RB["Retail Banking / Analytics Account"]
    MWAA["Amazon MWAA"]
    SM["SageMaker Domain / Pipelines"]
    MLS3[("S3 ML Artifacts")]
  end
  GIT -->|HTTPS| RM
  RW -->|"STS AssumeRole + ExternalId"| DP
  RW -->|"STS AssumeRole + ExternalId"| RB
  DP <-->|Private routed connectivity| NETWORK
  RB <-->|Private routed connectivity| NETWORK
  SHARED <-->|Private routed connectivity| NETWORK
  MWAA --> S3
  MWAA --> SM
  SM --> MLS3
~~~

## 3. Account responsibilities

| Logical account | Trách nhiệm | Thành phần |
|---|---|---|
| Shared Services | CI/CD execution, registry, Terraform state, runner operations | ECS, ECR, SSM Parameter Store, S3 state, CloudWatch Logs |
| Data Platform | Data Lake và data integration | S3, Glue, Lake Formation, DataSync, SQS, Lambda, API Gateway, monitoring |
| Retail Banking / Analytics | Orchestration và ML | MWAA, SageMaker Domain/User Profiles/Pipelines, S3, ECR, IAM, KMS, CloudWatch |
| Network | Connectivity dùng chung | VPC Endpoints, Private Hosted Zones, routing, Security Groups |

Khi triển khai thực tế, lấy account map từ cloud governance owner; không copy IDs từ môi trường nguồn.

## 4. Network foundation — Centralized VPC Endpoints

Tài liệu mô tả Centralized VPC Endpoints tại Network account. Member accounts định tuyến đến VPC chứa endpoints; Private Hosted Zone được chia sẻ để phân giải service endpoints; Security Groups cho phép HTTPS TCP/443 từ member VPCs.

Các endpoint groups được đề cập gồm IAM/STS/EC2, S3, Athena, Glue, Lake Formation, SQS, SageMaker, MWAA, ECR, ECS, SSM, CloudWatch Logs/Monitoring, Events, KMS, Secrets Manager, RAM, SNS, CloudFormation, ELB, ACM, API Gateway, Backup, Lambda, EFS và SES.

Không copy nguyên danh sách endpoint. Xác định API calls thực tế, chọn Interface Endpoint hay Gateway Endpoint, xác minh DNS, route tables, endpoint policy, Security Group và Region availability.

~~~mermaid
flowchart LR
  subgraph MEMBER["Member VPC"]
    TASK["Glue / EC2 / MWAA / Runner"]
    DNS["Route 53 Resolver"]
  end
  subgraph NET["Network Account"]
    PHZ["Private Hosted Zone"]
    EP["VPC Endpoint"]
    SG["Endpoint Security Group"]
  end
  TASK --> DNS --> PHZ --> EP
  TASK -->|TCP 443| SG
  SG --> EP --> AWS["AWS Service API"]
~~~

## 5. Data ingestion và Data Lake

### 5.1 DataSync path

Tài liệu mô tả DataSync Agent triển khai trên VMware On-Premises, sau đó đăng ký với AWS DataSync và tạo Agent, Source Location (NFS/SMB), Destination Location (S3), Task và schedule/options.

~~~mermaid
flowchart LR
  NAS["On-Prem NFS / SMB"] --> AG["DataSync Agent on VMware"]
  AG --> LOC["DataSync Locations"]
  LOC --> TASK["DataSync Task"]
  TASK --> S3["S3 Raw Zone"]
  S3 --> GLUE["Glue ETL / Catalog"]
  GLUE --> PREP["Prepared Zone"]
  PREP --> CUR["Curated Zone"]
~~~

Network team phải xác nhận connectivity theo deployment mode, agent, protocol và AWS documentation hiện hành. Không áp dụng port rule từ UAT một cách máy móc.

### 5.2 S3 zones

| Zone | Mục đích | Ví dụ xử lý |
|---|---|---|
| Raw | Lưu dữ liệu ingest gốc, hỗ trợ replay | Lưu source/time metadata, tránh overwrite tùy tiện |
| Prepared | Chuẩn hóa, làm sạch và chuẩn schema | Validate, deduplicate, normalize |
| Curated | Dataset phục vụ analytics/consumption | Partition, Parquet, quality contract |

Đây là logical layers; prefix, retention, schema, encryption và ownership cần thống nhất trong Data Governance. Chỉ dùng synthetic data trong learning repository.

## 6. Glue và Lake Formation

Tài liệu mô tả Terraform modules tạo Glue Catalog databases, Glue ETL Jobs cho Raw → Prepared, Glue Crawlers cho S3 prefixes, Lake Formation resources/permissions và registered S3 locations.

- **S3:** lưu object/data files.
- **Glue Data Catalog:** lưu metadata/schema/table/partition.
- **Glue ETL:** xử lý và chuyển đổi dữ liệu.
- **Lake Formation:** quản trị quyền truy cập data lake.
- **IAM:** kiểm soát identity và quyền gọi AWS APIs.

IAM, S3 bucket policy, KMS key policy và Lake Formation grants phải được thiết kế đồng bộ.

## 7. CI/CD và cross-account role assumption

GitLab Runner trong Shared Services assume role vào target accounts để deploy. Tài liệu sử dụng `sts:AssumeRole`, runner task role làm trusted principal và `sts:ExternalId` làm condition.

~~~mermaid
sequenceDiagram
  participant Dev as Developer
  participant GL as GitLab
  participant Runner as ECS Runner
  participant STS as AWS STS
  participant Target as Target Account
  Dev->>GL: Push / Merge
  GL->>Runner: Start CI job
  Runner->>STS: AssumeRole(RoleArn, ExternalId)
  STS->>Target: Validate trust + permission
  Target-->>Runner: Temporary credentials
  Runner->>Target: Terraform init / plan
  Runner->>Target: Apply after approval
  Runner->>Runner: Unset temporary credentials
~~~

Control points:
- Runner task role không nên là administrator cho mọi account.
- Target role trust đúng source role và giới hạn ExternalId.
- ExternalId giúp giảm confused-deputy risk, không thay authentication/least privilege.
- Temporary credentials chỉ dùng trong job scope và không log ra console.
- Tách role/policy theo account/workload; Production cần protected environment và approval.
- Lưu registration token trong secret store, không commit token.

## 8. Terraform structure và remote state

Tài liệu dùng một bộ code với environment folders và workspace:

~~~text
terraform-root/
├── backend.tf
├── providers.tf
├── variables.tf
├── locals.tf
├── data.tf
├── modules/
├── environments/
│   ├── uat/
│   │   ├── terraform.backend
│   │   └── terraform.tfvars
│   └── prd/
│       ├── terraform.backend
│       └── terraform.tfvars
└── service-*.tf
~~~

| File | Chức năng |
|---|---|
| `backend.tf` | Khai báo backend type |
| `terraform.backend` | Backend settings như bucket, key, Region, encryption và locking |
| `terraform.tfvars` | Giá trị biến theo environment |
| `providers.tf` | Provider source/version/configuration |
| `variables.tf` | Input variables |
| `locals.tf` | Local expressions |
| `data.tf` | Data sources đọc tài nguyên hiện hữu |
| `modules/` | Reusable resource modules |
| `service-*.tf` | AWS resources theo service/domain |

Tài liệu mô tả S3 remote backend ở Shared Services, versioning và TLS enforcement. State là dữ liệu nhạy cảm: giới hạn quyền, encryption, versioning, locking theo Terraform/backend version, backup và recovery.

**Workspace không phải security boundary.** Không dùng workspace thay account separation, IAM separation hay state access control. Production nên có isolated state boundary, approval và blast-radius control.

## 9. Pipeline lifecycle

Các stage được mô tả: (1) Bootstrap / Generate Pipeline; (2) Terraform Plan; (3) Compliance Check bằng TFLint/Trivy; (4) Deploy sau manual approval.

~~~mermaid
flowchart TD
  A["Commit / Push"] --> B["Generate dynamic pipeline"]
  B --> C["Terraform Plan"]
  C --> D["Compliance Check"]
  D --> E{"Approved?"}
  E -->|No| F["Stop / revise"]
  E -->|Yes| G["Terraform Apply"]
  G --> H["Post-deploy validation"]
  H --> I["Deployment audit"]
~~~

Các biến tham chiếu: `TF_VERSION`, `TF_CURRENT_WORKSPACE`, `TF_BACKEND_FILE`, `TF_VAR_FILE`, `ASSUME_ROLE_ARN`, `EXTERNAL_ID`, `ENVS`. Không đưa giá trị nhạy cảm/ARN thật vào public repo.

## 10. MWAA và SageMaker

### MWAA

Tài liệu mô tả MWAA execution role/policy, CloudWatch Log Groups, Security Group và MWAA environment. Có ghi chú cần request network access nếu muốn truy cập Airflow UI.

Khi vận hành, thiết kế private/public webserver mode, DAG deployment, dependency versions, scheduler/worker capacity, execution role, network egress, logs/alarms, retries, backfill, idempotency và recovery.

### SageMaker

Tài liệu mô tả SageMaker Domain, User Profiles, execution roles/policies, security group, KMS keys, CloudWatch Log Groups và ECR repositories cho pipeline images.

Phân biệt Domain execution role, user profile và training/inference roles. Quản lý model artifacts trong S3, container images trong ECR, image scanning, model lineage, model version, data drift và endpoint costs. Không ghi dữ liệu nhạy cảm trong notebook output/logs.

## 11. Operational controls

| Thành phần | Kiểm soát vận hành |
|---|---|
| ECS GitLab Runner | Kiểm tra manager/worker task state trước update; rollout có thể restart runner và interrupt jobs |
| S3 Terraform state | Versioning, restricted access, encryption, state locking và recovery |
| DataSync | Theo dõi task status/history, transferred bytes, verification và retry |
| Glue | Job metrics/logs, retries, bookmark strategy, quality và small files |
| SQS/Lambda | Visibility timeout, DLQ, retry/idempotency và alarm |
| MWAA | Scheduler/worker logs, DAG failures, queue depth và capacity |
| SageMaker | Training failures, endpoint latency/errors, artifacts và cost |
| CloudWatch/SNS | Alarm thresholds, subscriptions và incident runbook |

Trước khi update ECS Runner, drain runner, xác nhận không còn worker task/job đang chạy, thực hiện update và kiểm tra runner registration/test job trước khi enable lại.

## 12. Khi tái sử dụng cho tổ chức khác

Xác minh account ownership, Region/data residency, network/DNS, VPC endpoint types, IAM trust boundaries, SCP/permission boundaries, KMS ownership, data classification/retention, runner isolation, token handling, Terraform state recovery, service quotas, pricing, RTO/RPO và operational support.

## 13. Nguồn và giới hạn

Nguồn: *Tài liệu hướng dẫn triển khai hệ thống trên AWS (UAT), version 1.6*, Datum Limited / TPBank; cập nhật 11-Feb-2026.

- Trang 5–12: tools, accounts, DataSync, network, GitLab Runner, S3 Terraform state.
- Trang 13–20: deploy permissions, CI/CD assume roles và trust policies.
- Trang 21–33: Terraform layout, S3, Glue, Lake Formation, DataSync, SQS/Lambda, API, monitoring, backup.
- Trang 34–45: ECS-based GitLab Runner, ECR images và runner build.
- Trang 46–56: MWAA, SageMaker, S3, IAM, ECR và SNS.
- Trang 57–70: GitLab CI/CD pipeline, variables và deploy flow.

Tài liệu nguồn mô tả môi trường UAT tại thời điểm phát hành. Version, console screens, policies, ports, endpoints, permissions và pricing phải được kiểm tra lại theo AWS documentation và governance hiện hành trước khi dùng Production.