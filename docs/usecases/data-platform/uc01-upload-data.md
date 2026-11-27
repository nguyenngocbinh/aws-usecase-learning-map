# UC01 — Upload dữ liệu lên AWS S3

<small>DATA PLATFORM · HANDS-ON LAB · VERSION 1.0</small>

<badge>Prepared — AWS execution not yet verified</badge>

## 1. Business scenario

Một nhóm Data Engineering cần nhận file dữ liệu định kỳ từ máy Windows/on-premise và đưa lên AWS để xử lý tiếp. Lab dùng CSV synthetic mô phỏng danh mục khoản vay, không chứa dữ liệu khách hàng thật.

**Kết quả:** upload an toàn lên Amazon S3, kiểm tra object, bảo vệ bucket, ghi metadata và chạy lại bằng AWS CLI hoặc Python Boto3.

## 2. Learning objectives

- Phân biệt object storage với block/file storage.
- Tạo S3 bucket private-by-default.
- Xác thực bằng IAM role/profile, không hard-code access key.
- Upload bằng Console, AWS CLI và Boto3.
- Bật versioning, encryption, public access block và lifecycle.
- Kiểm tra object, metadata, CloudTrail data events và lỗi quyền.
- Ước tính cost drivers và xóa tài nguyên sau lab.

## 3. Architecture

### 3.1 Luồng upload cơ bản

~~~mermaid
flowchart LR
  subgraph LOCAL["Local / On-prem"]
    FILE["CSV / Parquet"]
    CLI["AWS CLI v2"]
    PY["Python + Boto3"]
  end
  subgraph AWS["AWS Account · Learning Region"]
    IAM["IAM Role / Profile"]
    S3["Amazon S3 Bucket"]
    ENC["Default encryption"]
    VER["Versioning"]
    CT["CloudTrail data events"]
  end
  FILE --> CLI
  FILE --> PY
  CLI --> IAM
  PY --> IAM
  IAM -->|"PutObject: scoped prefix"| S3
  S3 --> ENC
  S3 --> VER
  S3 -. audit .-> CT
~~~

### 3.2 Trust boundary và quyền truy cập

~~~mermaid
flowchart TB
  HUMAN["Learner identity / IAM Identity Center"] -->|"Temporary credentials"| ROLE["Lab upload role"]
  ROLE -->|"PutObject scoped prefix"| PREFIX["arn:aws:s3:::bucket/landing/*"]
  ROLE -->|"ListBucket with prefix condition"| BUCKET["S3 bucket"]
  PUBLIC["Public internet"] -. "Blocked" .-> BUCKET
~~~

### 3.3 Data layout

~~~text
s3://<bucket-name>/
  landing/
    source_system=loan_demo/
      ingest_date=YYYY-MM-DD/
        loans.csv
  rejected/
  processed/
~~~

Không đưa account ID, customer identifier thật hoặc dữ liệu nhạy cảm vào tên bucket/key. Dùng prefix nhất quán để hỗ trợ downstream ETL.

## 4. Thành phần AWS sử dụng

Use case này tập trung vào luồng upload file lên Amazon S3. Phần giải thích khái niệm chuyên sâu về S3, IAM, CLI/SDK, KMS và CloudTrail thuộc AWS Knowledge Base.

### 4.1 Amazon S3

- **Vai trò:** lưu trữ file nguồn dưới dạng object trong bucket.
- **Cấu hình sử dụng:** private bucket, prefix theo source/date, Block Public Access, default encryption, Versioning và Lifecycle khi phù hợp.
- **Thao tác chính:** tạo bucket, upload object, kiểm tra object metadata và xác minh nội dung.

### 4.2 IAM

- **Vai trò:** xác thực learner/workload và giới hạn quyền upload.
- **Quyền chính:** `s3:PutObject` trên prefix đích; `s3:ListBucket` với prefix condition khi cần; quyền KMS tương ứng nếu dùng SSE-KMS.
- **Nguyên tắc:** ưu tiên IAM Identity Center/temporary credentials hoặc role; không hard-code access key.

### 4.3 AWS CLI và Python Boto3

- **AWS CLI:** upload và kiểm tra object từ terminal (`aws s3 cp`, `aws s3api head-object`).
- **Boto3:** tích hợp upload vào Python application/ETL, xử lý exception và retry.
- Cả hai sử dụng credential provider chain, không ghi credentials vào source code.

### 4.4 KMS và CloudTrail

- **KMS:** chỉ sử dụng SSE-KMS khi cần customer-managed key hoặc key governance; nếu không, đánh giá SSE-S3.
- **CloudTrail:** bật S3 data events khi use case yêu cầu audit object-level API activity; cân nhắc chi phí event.

## 5. Alternatives — chọn đúng storage/transfer service

| Lựa chọn | Dùng khi | Không phù hợp khi |
|---|---|---|
| Amazon S3 | Object/file ingestion, data lake, backup, artifacts | Cần block device hoặc POSIX filesystem |
| Amazon EBS | Block storage gắn với EC2, low-latency disk | Chia sẻ file/object giữa nhiều hệ thống |
| Amazon EFS | Shared NFS filesystem cho Linux workloads | Lưu object/data lake qua S3 API |
| Amazon FSx | Cần Windows File Server, Lustre, ONTAP hoặc OpenZFS | Chỉ cần upload object đơn giản |
| AWS DataSync | Transfer/sync lượng lớn dữ liệu giữa on-prem/NAS và AWS | Một file nhỏ upload thủ công |
| AWS Transfer Family | Đối tác cần SFTP/FTPS/FTP managed endpoint | Ứng dụng đã dùng được S3 API/HTTPS |
| AWS Snow Family | Offline/limited network, transfer rất lớn | Data upload nhỏ qua internet |

**Decision rule:** ứng dụng mới → S3 API/CLI/SDK; đồng bộ file server hiện hữu → đánh giá DataSync; đối tác cần SFTP → Transfer Family; mạng yếu và lượng dữ liệu lớn → đánh giá Snow Family. So sánh network, security, operational effort và total cost.

## 6. Prerequisites

- AWS learning account riêng, MFA và billing budget/alert.
- Chọn Region; ví dụ ap-southeast-1 nếu service availability và yêu cầu dữ liệu phù hợp.
- AWS CLI v2, Python 3.10+ và Boto3.
- Identity dùng IAM Identity Center/role hoặc profile SSO.
- Chỉ dùng CSV synthetic trong repo.

### 6.1 Kiểm tra identity

~~~bash
aws --version
aws sts get-caller-identity
aws configure list
~~~

Nếu dùng IAM Identity Center:

~~~bash
aws configure sso
aws sso login --profile aws-learning
aws sts get-caller-identity --profile aws-learning
~~~

Không lưu access key dài hạn nếu có lựa chọn federation/SSO.

## 7. Hands-on lab

### Lab 01 — Tạo bucket bằng Console

1. Mở [Amazon S3 Console](https://console.aws.amazon.com/s3/).
2. Chọn Create bucket; tên globally unique, ví dụ aws-uc01-<random-suffix>.
3. Chọn Region đã thống nhất.
4. Giữ Block all public access bật.
5. Object Ownership: Bucket owner enforced (ACLs disabled).
6. Bật Versioning.
7. Default encryption: SSE-S3 cho lab cơ bản.
8. Tạo bucket; không upload dữ liệu thật.

### Lab 02 — Upload bằng Console

1. Mở bucket → tạo prefix landing/loan_demo/ingest_date=YYYY-MM-DD/.
2. Upload sample_loans.csv.
3. Kiểm tra object size, last modified, encryption và version ID.
4. Upload lại cùng key khi versioning bật; quan sát version history.

### Lab 03 — Upload bằng AWS CLI

Tạo bucket qua Console hoặc Terraform. Thay bucket name bằng bucket của learning account:

~~~bash
export AWS_REGION="ap-southeast-1"
export BUCKET="your-unique-bucket-name"
export KEY="landing/loan_demo/sample_loans.csv"

aws s3 cp usecases/UC01/data/sample_loans.csv "s3://$BUCKET/$KEY" --region "$AWS_REGION" --sse AES256
aws s3api head-object --bucket "$BUCKET" --key "$KEY" --region "$AWS_REGION"
~~~

Trên PowerShell:

~~~powershell
$env:AWS_REGION = "ap-southeast-1"
$env:BUCKET = "your-unique-bucket-name"
$env:KEY = "landing/loan_demo/sample_loans.csv"
aws s3 cp .\usecases\UC01\data\sample_loans.csv "s3://$env:BUCKET/$env:KEY" --region $env:AWS_REGION --sse AES256
aws s3api head-object --bucket $env:BUCKET --key $env:KEY --region $env:AWS_REGION
~~~

### Lab 04 — Upload bằng Python Boto3

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r usecases/UC01/requirements.txt
$env:AWS_PROFILE = "aws-learning"
$env:AWS_REGION = "ap-southeast-1"
$env:S3_BUCKET = "your-unique-bucket-name"
$env:S3_PREFIX = "landing/loan_demo"
python usecases/UC01/src/upload_to_s3.py usecases/UC01/data/sample_loans.csv
python usecases/UC01/src/verify_s3_object.py
~~~

Code dùng Boto3 default credential chain, không truyền secret qua command line và không ghi access key trong source.

### Lab 05 — Kiểm tra và negative tests

~~~bash
aws s3 ls "s3://$BUCKET/landing/loan_demo/" --recursive
aws s3api get-bucket-versioning --bucket "$BUCKET"
aws s3api get-public-access-block --bucket "$BUCKET"
aws s3api get-bucket-encryption --bucket "$BUCKET"
~~~

Thực hành có kiểm soát:
- Dùng role chỉ có quyền upload vào prefix được phép.
- Thử upload sang prefix khác để xác nhận AccessDenied.
- Thử head-object khi chưa có quyền đọc để quan sát lỗi.
- Không tắt Block Public Access và không tạo bucket public.

## 8. Terraform — repeatable bucket

Mã nguồn: [usecases/UC01/infrastructure/terraform](https://github.com/nguyenngocbinh/aws-usecase-learning-map/tree/feature/uc01-s3-upload-lab/usecases/UC01/infrastructure/terraform).

~~~bash
cd usecases/UC01/infrastructure/terraform
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
~~~

Kiểm tra kỹ account, Region và resource name trước apply. Terraform state chứa metadata hạ tầng; không commit state lên Git.

## 9. Expected results

- [ ] AWS identity đúng learning account.
- [ ] Bucket ở Region đã chọn, public access bị block.
- [ ] Versioning bật và encryption default được cấu hình.
- [ ] File CSV có mặt trong prefix yêu cầu.
- [ ] head-object trả về ContentLength và ServerSideEncryption.
- [ ] Boto3 script in bucket, key, file size và SHA-256 local.
- [ ] Negative test chứng minh role không ghi ngoài prefix.
- [ ] Không có access key/secret trong repo hoặc log.

## 10. Security checklist

- Private-by-default; Block Public Access bật ở account và bucket.
- Dùng IAM role/SSO, least privilege và temporary credentials.
- Bucket owner enforced; không dựa vào ACL.
- Bật default encryption; SSE-KMS khi có yêu cầu quản trị key cụ thể.
- Dùng TLS; bucket policy deny insecure transport.
- Không log dữ liệu nhạy cảm hoặc secrets.
- Bật CloudTrail S3 data events có chọn lọc nếu cần object-level audit; cân nhắc chi phí.
- Versioning hỗ trợ phục hồi object overwrite/delete nhưng không thay thế backup/retention.

## 11. Cost model

| Thành phần | Pricing dimension cần kiểm tra |
|---|---|
| S3 storage | GB-month theo storage class |
| PUT/COPY/POST/LIST | Request count |
| GET/HEAD | Request count |
| Data transfer | Transfer out/cross-Region; kiểm tra đường truyền |
| Versioning | Mỗi object version chiếm storage |
| Lifecycle | Transition/request và storage class minimum duration |
| SSE-KMS | KMS key và API request nếu chọn SSE-KMS |
| CloudTrail data events | Event volume/Trail/Lake configuration |

Dùng [AWS Pricing Calculator](https://calculator.aws/) và [S3 pricing](https://aws.amazon.com/s3/pricing/) theo Region thực tế. Không đưa con số cố định khi chưa biết volume, request rate, retention và data transfer.

## 12. Troubleshooting

| Symptom | Nguyên nhân thường gặp | Kiểm tra |
|---|---|---|
| AccessDenied | IAM/bucket policy explicit deny hoặc thiếu action | sts get-caller-identity, policy simulator, bucket policy |
| NoSuchBucket | Sai bucket name hoặc account/Region | s3api head-bucket |
| Wrong endpoint | Region không đúng | Kiểm tra bucket Region và CLI --region |
| KMS AccessDenied | Thiếu key policy/grant/permissions | Kiểm tra key ARN, Region, key policy |
| ExpiredToken | SSO/session hết hạn | aws sso login --profile ... |
| Slow upload | File lớn, network, concurrency | Multipart, retry và network |
| Object overwritten | Ghi cùng key; versioning chưa bật | Kiểm tra versioning và object versions |

## 13. Cleanup

Nếu tạo bucket bằng Terraform:

~~~bash
terraform destroy
~~~

Nếu tạo thủ công, trước hết xác minh đúng bucket test:

~~~bash
aws s3 ls "s3://$BUCKET" --recursive
aws s3api get-bucket-versioning --bucket "$BUCKET"
~~~

Xóa object và tất cả versions/delete markers trước khi xóa bucket. Cleanup là destructive; chỉ chạy với bucket test riêng, không dùng wildcard hoặc biến chưa kiểm tra.

Sau lab: xóa object versions/delete markers, bucket, IAM role/policy riêng; kiểm tra AWS Billing/Cost Explorer để phát hiện tài nguyên còn tồn tại.

## 14. Knowledge check

1. Vì sao S3 không tương đương EBS hoặc EFS?
2. Khi nào nên dùng DataSync thay vì AWS CLI?
3. Vì sao nên dùng role/SSO thay vì access key dài hạn?
4. Bucket policy và IAM identity policy khác nhau thế nào?
5. SSE-S3 khác SSE-KMS ở điểm nào?
6. Versioning bảo vệ tình huống nào và không thay thế điều gì?
7. CloudTrail management events khác S3 data events ra sao?
8. Tại sao không public bucket để upload dễ hơn?
9. Pricing S3 gồm dimension nào ngoài GB-month?
10. Làm thế nào xác minh upload thành công mà không tải file về?

## 15. Official references

- [Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [S3 security best practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [S3 default encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [AWS CLI S3 reference](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [Boto3 S3 upload guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html)
- [AWS IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)

**Last reviewed:** 2026-11-20. Kiểm tra lại pricing, service availability, quotas và tài liệu chính thức trước mỗi lần chạy lab.
