# AWS Use Case Learning Map

<div class="hero" markdown>

<span class="hero-kicker">HANDS-ON CLOUD LEARNING · 2026</span>

# Learn AWS by building real systems.

Từ nền tảng dữ liệu đến Machine Learning, CI/CD và vận hành production. Học từng dịch vụ qua use case thực tế, kiến trúc trực quan và lab có thể chạy lại.

<div class="hero-actions" markdown>
[🚀 Bắt đầu lộ trình](roadmap/index.md){ .md-button .md-button--primary }
[📋 Xem kế hoạch dự án](project/todos.md){ .md-button }
</div>

<div class="hero-meta">
  <span>12 USE CASES</span><span>5 LEARNING DOMAINS</span><span>HANDS-ON FIRST</span>
</div>
</div>

## Chọn hành trình của bạn

<div class="domain-grid" markdown>

<div class="domain-card data" markdown>
<span class="domain-index">A / 01–03</span>
<h3>Data Platform</h3>
<p>Đưa dữ liệu lên AWS, xây Data Lake, ETL và migration database.</p>
<strong>3 use cases</strong><br>
[Khám phá Data Platform →](usecases/data-platform/uc01-upload-data.md)
</div>

<div class="domain-card ml" markdown>
<span class="domain-index">B / 04–06</span>
<h3>Machine Learning</h3>
<p>Training, quản lý phiên bản, deploy API, batch scoring và monitoring.</p>
<strong>3 use cases</strong><br>
[Khám phá Machine Learning →](usecases/machine-learning/uc04-model-training.md)
</div>

<div class="domain-card devops" markdown>
<span class="domain-index">C / 07–09</span>
<h3>DevOps</h3>
<p>Kết nối GitHub/GitLab, tự động build, test và deploy.</p>
<strong>3 use cases</strong><br>
[Khám phá DevOps →](usecases/devops/uc07-github-aws.md)
</div>

<div class="domain-card ops" markdown>
<span class="domain-index">D / 10–11</span>
<h3>Operations</h3>
<p>Lập lịch pipeline, giám sát hệ thống, cảnh báo và xử lý incident.</p>
<strong>2 use cases</strong><br>
[Khám phá Operations →](usecases/operations/uc10-scheduling.md)
</div>

<div class="domain-card security" markdown>
<span class="domain-index">E / 12</span>
<h3>Security & Governance</h3>
<p>IAM, encryption, backup, disaster recovery và quản trị.</p>
<strong>1 use case</strong><br>
[Khám phá Security →](usecases/security/uc12-security-backup-dr.md)
</div>

</div>

## Learning path

<div class="path-grid" markdown>
<div class="path-step" markdown>
<span>01</span>
<h3>Foundation & Data</h3>
<p>UC01 → UC02 → UC03</p>
</div>
<div class="path-step" markdown>
<span>02</span>
<h3>Machine Learning</h3>
<p>UC04 → UC05 → UC06</p>
</div>
<div class="path-step" markdown>
<span>03</span>
<h3>DevOps & Automation</h3>
<p>UC07 → UC08 → UC09 → UC10</p>
</div>
<div class="path-step" markdown>
<span>04</span>
<h3>Production Ready</h3>
<p>UC11 → UC12</p>
</div>
</div>

## Reference architecture — Retail Credit Risk Platform

Dùng dữ liệu **synthetic** để thực hành trọn luồng Data Engineering → ML → Operations. Không sử dụng dữ liệu khách hàng hoặc cấu hình nội bộ.

```mermaid
flowchart LR
    SRC["On-prem DB / Files"] --> ING["DMS / CLI / SDK"]
    ING --> RAW[("S3 · Raw")]
    RAW --> ETL["Glue ETL"]
    ETL --> CUR[("S3 · Curated")]
    CUR --> CAT["Glue Catalog"]
    CAT --> ATH["Athena"]
    CUR --> TRAIN["SageMaker AI"]
    TRAIN --> REG["Model Registry"]
    REG --> INF["Inference API"]
    REG --> BATCH["Batch Scoring"]
    INF --> OUT[("Scoring Results")]
    BATCH --> OUT
    OUT --> OBS["CloudWatch / Alerts"]
    CICD["GitHub / GitLab CI/CD"] -. deploy .-> ETL
    CICD -. deploy .-> INF
```

## Cách học một use case

1. **Understand** — đọc business scenario, mục tiêu và prerequisites.
2. **Design** — xem architecture, data flow và lựa chọn dịch vụ.
3. **Compare** — phân tích dịch vụ thay thế và trade-offs.
4. **Build** — làm lab theo từng bước bằng Console, CLI, SDK và Terraform.
5. **Validate** — kiểm tra output, test, logs và failure scenarios.
6. **Operate & clean up** — theo dõi chi phí, vận hành và xóa tài nguyên.

## Nguyên tắc nội dung

- Tiếng Việt, giữ nguyên thuật ngữ kỹ thuật tiếng Anh.
- Mỗi AWS service có 10 câu hỏi WH và so sánh lựa chọn thay thế.
- Sơ đồ có mã nguồn Mermaid/Draw.io; hình có chú thích và nguồn.
- Lab ưu tiên synthetic data, least privilege, repeatability và cleanup.
- Chi phí là phần bắt buộc, không mặc định tài nguyên AWS là miễn phí.

> **Trạng thái hiện tại:** Portal foundation và implementation backlog đang được khởi tạo. Các use case sẽ được đánh dấu hoàn thành sau khi nội dung và lab được kiểm chứng.
