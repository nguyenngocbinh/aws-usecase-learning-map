# UC09 — CI/CD cho AWS Infrastructure và Workload

> **UC09 · DEVOPS · HANDS-ON GUIDE**
>
> Tổng hợp pattern Terraform/GitLab CI/CD trong tài liệu AWS UAT v1.6 và mở rộng sang GitHub OIDC. UAT dùng GitLab Runner/ECS trong Shared Services; nội dung dưới đây là hướng dẫn độc lập, không sử dụng thông tin nội bộ.

## 1. Business scenario

Platform team cần quản lý AWS infrastructure bằng code, review thay đổi qua Git, tự động validation/security checks, tạo Terraform plan, yêu cầu approval trước apply và audit/rollback.

## 2. Reference pipeline

~~~mermaid
flowchart TD
  DEV["Developer Push / Pull Request"] --> LINT["Format + Validate + Tests"]
  LINT --> SEC["Security Scan"]
  SEC --> PLAN["Terraform Plan"]
  PLAN --> REVIEW["Code Review / Plan Review"]
  REVIEW --> APPROVE{"Protected Environment Approval"}
  APPROVE -->|Approved| APPLY["Terraform Apply"]
  APPROVE -->|Rejected| STOP["Stop Pipeline"]
  APPLY --> VERIFY["Post-deploy Validation"]
  VERIFY --> AUDIT["Deployment Record / CloudTrail"]
~~~

## 3. Design decisions

| Decision | Starting point | Trade-off |
|---|---|---|
| Repository | GitHub or GitLab | Theo source control standard |
| AWS authentication | OIDC federation | Cần trust conditions/provider |
| Terraform state | S3 remote backend | Bootstrap và backend permissions |
| Environments | Separate role/state boundaries | Nhiều cấu hình nhưng giảm blast radius |
| Validation | fmt, validate, TFLint, Trivy | Tool maintenance/false positives |
| Deployment | Reviewed plan artifact | Cần kiểm soát artifact lifecycle |
| Production approval | Protected environment/manual gate | Human control và latency |

## 4. Cross-account architecture

~~~mermaid
flowchart LR
  subgraph SCM["Git Provider"]
    REPO["Repository"]
    PIPE["CI Pipeline"]
  end
  subgraph TOOL["Tools / Shared Services"]
    RUN["Hosted Runner or ECS Runner"]
    STATE[("S3 Terraform State")]
  end
  subgraph TARGET["Target AWS Account"]
    OIDC["OIDC Provider / STS"]
    ROLE["Deployment IAM Role"]
    RES["AWS Resources"]
  end
  REPO --> PIPE --> RUN
  RUN -->|OIDC JWT| OIDC
  OIDC -->|AssumeRoleWithWebIdentity| ROLE
  ROLE --> RES
  RUN --> STATE
~~~

UAT v1.6 mô tả ECS GitLab Runner manager/worker trong Shared Services; worker assume target role qua `sts:AssumeRole` và `ExternalId`. Nếu Git provider hỗ trợ OIDC, đánh giá federation trực tiếp để tránh giữ AWS access key dài hạn.

## 5. Pipeline stages

### Stage 1 — Validate

~~~bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
~~~

### Stage 2 — Lint and security

~~~bash
tflint --recursive
trivy config --severity HIGH,CRITICAL .
~~~

Pin tool versions và review security exceptions.

### Stage 3 — Plan

~~~bash
terraform init -backend-config=environments/uat/backend.hcl
terraform workspace select uat || terraform workspace new uat
terraform plan -var-file=environments/uat/terraform.tfvars -out=tfplan
terraform show -no-color tfplan
~~~

Review create/update/delete. Bảo vệ `tfplan`, plan JSON và state như artifacts nhạy cảm; giới hạn download, expiry ngắn và không expose secrets.

### Stage 4 — Approval and apply

~~~bash
terraform apply tfplan
~~~

Apply đúng plan artifact đã review. Production sử dụng protected branch/environment, approvers và audit.

### Stage 5 — Post-deployment

- Kiểm tra resource state và health checks.
- Kiểm tra CloudTrail deployment principal/actions.
- Kiểm tra logs/metrics/alarms.
- Ghi commit SHA, pipeline run, workspace/account/Region và plan artifact hash.
- Có rollback/recovery plan theo từng resource/service.

## 6. GitHub Actions — OIDC skeleton

Cần cấu hình IAM OIDC provider và role trust policy ở AWS trước. Trust policy minh họa; thay placeholder theo repository, environment và account thực tế:

~~~json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "GitHubActionsOIDC",
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:<GITHUB_OWNER>/<GITHUB_REPO>:environment:uat"
      }
    }
  }]
}
~~~

Workflow skeleton:

~~~yaml
name: terraform-uat
on:
  pull_request:
    paths: ["infrastructure/**"]
  push:
    branches: [main]
    paths: ["infrastructure/**"]
  workflow_dispatch:
permissions:
  contents: read
  id-token: write
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.13.5"
      - run: terraform -chdir=infrastructure/terraform fmt -check -recursive
      - run: terraform -chdir=infrastructure/terraform init -backend=false
      - run: terraform -chdir=infrastructure/terraform validate
  plan:
    needs: validate
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.13.5"
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_UAT_ROLE_ARN }}
          aws-region: ap-southeast-1
      - run: aws sts get-caller-identity
      - run: |
          terraform -chdir=infrastructure/terraform init
          terraform -chdir=infrastructure/terraform plan -var-file=environments/uat/terraform.tfvars
~~~

Đây là skeleton học tập. Production phải pin GitHub Actions bằng full commit SHA, giới hạn trust `sub` theo repo/environment/branch, bật Environment protection và không cấp AWS credentials cho untrusted fork code. Không dùng `pull_request_target` để chạy code không tin cậy với quyền AWS.

## 7. GitLab CI — pattern theo tài liệu UAT

Tài liệu UAT v1.6 tổ chức:

~~~text
.gitlab-ci.yml
cicd/
  jobs.yml
  rules.yml
  pipeline.yml
~~~

- `jobs.yml`: reusable hidden jobs qua `!reference`.
- `rules.yml`: điều kiện trigger theo branch/event.
- `pipeline.yml`: dynamic pipeline generator.
- `.gitlab-ci.yml`: entrypoint, stages, variables và child pipeline trigger.

Các stage được mô tả: **Terraform Plan → Compliance Check → Deploy**. Variables tham chiếu: `TF_VERSION`, `TF_CURRENT_WORKSPACE`, `TF_BACKEND_FILE`, `TF_VAR_FILE`, `ASSUME_ROLE_ARN`, `EXTERNAL_ID`, `ENVS`.

Authentication models:
- **OIDC federation:** GitLab ID token → `AssumeRoleWithWebIdentity`; trust condition giới hạn project/ref/audience.
- **Runner role → AssumeRole:** runner task role được target role trust; giới hạn ExternalId và policy scope.

Không trộn hai model vô thức. Tránh lưu AWS access keys dài hạn trong CI variables.

## 8. Terraform remote state

UAT v1.6 tạo S3 bucket riêng tại Shared Services, bật versioning, yêu cầu TLS và cấp quyền cho deployment roles. Với Terraform hiện hành, xác minh locking support và cú pháp backend theo version đang dùng.

~~~hcl
bucket       = "your-learning-tfstate-bucket"
key          = "platform/uat/terraform.tfstate"
region       = "ap-southeast-1"
encrypt      = true
use_lockfile = true
~~~

Bootstrap bucket ngoài stack cần state bucket; bật versioning, encryption, Block Public Access, TLS-only policy và least-privilege access.

## 9. IAM least-privilege checklist

- CI principal chỉ assume đúng deployment role.
- Trust policy giới hạn source identity/repository/project/ref/audience.
- Deployment role giới hạn actions/resources phù hợp stack.
- Backend policy tách `ListBucket` (prefix condition) và object read/write trên state key.
- KMS permissions chỉ với key cụ thể.
- Deny Production apply nếu không qua protected environment/approved pipeline.
- Temporary credentials; không echo token.
- Audit bằng CloudTrail và CI logs.

## 10. Runner operations với ECS/Fargate

UAT v1.6 mô tả runner manager/worker tasks, ECR images, SSM Parameter Store cho registration token, CloudWatch Log Groups, ECS cluster/services và Security Group cho manager-worker connectivity.

Trước update runner infrastructure: kiểm tra pipeline đang chạy; drain runner; xác nhận active worker tasks = 0; update image/task definition/service; kiểm tra registration và test job; enable lại runner; theo dõi CloudWatch logs.

## 11. Troubleshooting

| Symptom | Nguyên nhân có thể | Cách xử lý |
|---|---|---|
| AccessDenied khi assume role | Trust policy, OIDC claims, ExternalId sai | Kiểm tra caller identity, `sub`, `aud`, role ARN |
| No credentials | Runner thiếu identity/session | Kiểm tra OIDC token hoặc task role |
| Terraform state lock | Job khác đang apply hoặc lock stale | Xác minh process; không force-unlock mù |
| Plan ngoài mong đợi | Wrong workspace/vars/backend/account | Log account, workspace, backend key, var file |
| Missing plan artifact | Artifact expired/dependency sai | Giữ artifact đủ lâu và bind đúng job |
| TFLint fail | Provider/module rule hoặc syntax | Pin plugin/version và xử lý findings |
| Trivy findings | IaC misconfiguration | Review severity/context, documented exception |
| Runner offline | ECS task, token, network hoặc ECR issue | ECS events, CloudWatch, SSM, connectivity |

## 12. Rollback và recovery

Terraform infrastructure rollback thường là corrective commit và plan/apply mới, không tự động đảo ngược mọi thay đổi. Giữ Git history và artifacts gắn commit. Với destructive change, review replacement/destroy, backup và recovery trước. Tách database migration rollback khỏi infra deployment rollback.

## 13. Knowledge check

1. OIDC khác access key tĩnh thế nào?
2. `AssumeRole` và `AssumeRoleWithWebIdentity` khác nhau ở đâu?
3. Vì sao target role phải giới hạn Principal và Condition?
4. `ExternalId` giải quyết rủi ro nào?
5. Terraform state cần controls gì?
6. Vì sao phải review Plan trước Apply?
7. Làm sao bảo đảm Apply đúng plan đã duyệt?
8. Vì sao workspace không phải security boundary?
9. Tại sao không chạy untrusted PR với AWS credentials?
10. Vì sao update ECS GitLab Runner cần kiểm tra active worker jobs?

## 14. Official references

- [GitHub OIDC in AWS](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [GitLab AWS OIDC](https://docs.gitlab.com/ci/cloud_services/aws/)
- [IAM role trust policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_manage_modify.html)
- [AWS STS AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html)
- [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3)
- [Terraform workspaces](https://developer.hashicorp.com/terraform/cli/workspaces)
- [GitHub Actions environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [GitLab CI/CD environments](https://docs.gitlab.com/ci/environments/)
- [Trivy IaC scanning](https://trivy.dev/latest/docs/target/misconfiguration/)
- [TFLint](https://github.com/terraform-linters/tflint)

## 15. Acceptance criteria

- [ ] PR pipeline chạy format/validate/tests.
- [ ] CI lấy AWS temporary credentials, không commit access keys.
- [ ] Trust policy scoped theo repository/project/environment.
- [ ] Plan artifact được giữ an toàn và review.
- [ ] Apply cần protected approval cho environment mục tiêu.
- [ ] Audit record xác định principal, commit và resources changed.
- [ ] Runner maintenance không interrupt jobs đang chạy.
- [ ] Cleanup và recovery được mô tả.