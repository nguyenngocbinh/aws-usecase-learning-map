# Project implementation backlog

This is the source of truth for the AWS Use Case Learning Map delivery plan. Check an item only after its acceptance criteria have been verified in the repository or deployed site.

## Milestone 0 — Product decisions and repository foundation

- [ ] Confirm the site name, public audience, language policy, and GitHub Pages URL.
- [ ] Keep the learning content in Vietnamese with English AWS service names and searchable English keywords.
- [ ] Use one repository and one documentation website for all 12 use cases.
- [ ] Keep documentation in `docs/`, runnable labs in `usecases/`, and shared IaC in `infrastructure/`.
- [ ] Define contribution rules, license, code-of-conduct expectations, and change log.
- [ ] Add a security policy: no credentials, real customer data, or production configuration.
- [ ] Define a consistent status vocabulary: Planned, In progress, Lab verified, Published.

**Acceptance:** repository structure and contribution/safety conventions are documented.

## Milestone 1 — Documentation portal and visual design

- [ ] Configure Material for MkDocs, site metadata, navigation, search, code copy, tabs, and light/dark themes.
- [ ] Create a polished homepage with learning path, domain cards, progress/status labels, and quick-start links.
- [ ] Create a roadmap page explaining prerequisites and recommended learning order.
- [ ] Create AWS fundamentals pages: account, IAM, Region/AZ, CLI, budget, and cost hygiene.
- [ ] Create reusable use-case and AWS-service page templates.
- [ ] Enable Mermaid diagrams and add at least one architecture/data-flow diagram to each use-case overview as content is authored.
- [ ] Add image attribution conventions and an image register (source URL, creator/provider, license/terms, retrieval date).
- [ ] Prefer original Mermaid/Draw.io diagrams and official AWS Architecture Center/service documentation; use external images only when reuse terms permit.
- [ ] Add responsive image styling, captions, alt text, and local optimized assets.
- [ ] Add glossary, service catalog, comparison pages, and troubleshooting index.

**Acceptance:** local `mkdocs build --strict` succeeds; navigation has no broken pages; homepage and at least one complete sample use case render correctly on mobile and desktop.

## Milestone 2 — AWS service knowledge base

For each service used in the 12 use cases:

- [ ] What — definition and core capability.
- [ ] Why — business/technical reason to use it.
- [ ] When — suitable and unsuitable scenarios.
- [ ] Where — Region, Availability Zone, edge, network, and placement considerations.
- [ ] Who — personas, responsibilities, and IAM actors.
- [ ] Which — relevant service tiers, deployment modes, and configuration choices.
- [ ] How — console, CLI, SDK, and IaC implementation.
- [ ] How much — pricing dimensions, cost drivers, estimation example, and cost caveats.
- [ ] What if — failure modes, limits, recovery, and troubleshooting.
- [ ] How compared — alternatives, decision matrix, trade-offs, and selection rationale.
- [ ] Link to official AWS documentation and pricing pages; record the date checked.

**Acceptance:** every service page has all 10 WH sections and current official references.

## Milestone 3 — Use case content and labs

Each use case must contain: business scenario, prerequisites, architecture, data flow, AWS service selection, alternatives, security model, cost model, step-by-step lab, runnable code, expected output, automated validation, troubleshooting, cleanup, and knowledge check.

### Group A — Data Platform
- [ ] UC01 — Upload data to AWS (S3, IAM, CLI, Boto3, encryption, lifecycle, audit).
- [ ] UC02 — Build a Data Lake and ETL (S3 zones, Glue, Data Catalog, Athena, orchestration).
- [ ] UC03 — Database migration (DMS, SCT where applicable, RDS SQL Server vs SQL Server on EC2, validation and cutover).

### Group B — Machine Learning
- [ ] UC04 — Train and manage a model (S3, SageMaker AI, model artifacts, registry, reproducibility).
- [ ] UC05 — Deploy a model as an API (SageMaker endpoint or container API, API Gateway/Lambda where appropriate, auth, latency and scaling).
- [ ] UC06 — Batch scoring and monitoring (Batch Transform or scheduled processing, drift/quality signals, alerts and cost controls).

### Group C — DevOps
- [ ] UC07 — Connect GitHub to AWS (GitHub OIDC and/or CodeConnections; least privilege).
- [ ] UC08 — Connect GitLab to AWS (OIDC federation, STS role assumption, protected environments).
- [ ] UC09 — Automated CI/CD (test, build, scan, publish, deploy, approval, rollback).

### Group D — Operations
- [ ] UC10 — Scheduling and orchestration (EventBridge Scheduler, Step Functions, Glue Workflows; retries and idempotency).
- [ ] UC11 — Monitoring, alerts, and incidents (CloudWatch, CloudTrail, SNS, runbooks, incident exercises).

### Group E — Security & Governance
- [ ] UC12 — Security, backup, and disaster recovery (IAM, KMS, Secrets Manager, AWS Backup, S3 versioning/replication, RPO/RTO tests).

**Acceptance per UC:** a learner can follow the lab in a clean learning account, verify expected results, and remove billable resources.

## Milestone 4 — Runnable code and infrastructure

- [ ] Add Python/Boto3 examples with type hints, error handling, and safe configuration.
- [ ] Add SQL and sample synthetic datasets where relevant.
- [ ] Add Terraform modules/examples with pinned provider constraints and documented inputs/outputs.
- [ ] Add YAML examples with schema/format validation.
- [ ] Add tests and sample expected outputs.
- [ ] Add setup, deploy, validate, and cleanup scripts.
- [ ] Separate low-cost default labs from optional higher-cost labs.
- [ ] Document quotas, regional availability, service prerequisites, and alternative paths.

**Acceptance:** code checks pass; no secret scanning findings; each lab has a tested cleanup path.

## Milestone 5 — Automation, publishing, and quality

- [ ] Configure GitHub Pages to use GitHub Actions as the publishing source.
- [ ] Add documentation workflow: install dependencies, build with strict mode, upload Pages artifact, deploy.
- [ ] Add pull-request validation for Markdown links, YAML, Python tests, and Terraform format/validate.
- [ ] Pin or update third-party GitHub Actions according to a documented dependency policy; prefer immutable commit SHAs for production workflows.
- [ ] Add dependency update process and security scanning.
- [ ] Add deployment badge and published-site link after first successful deployment.
- [ ] Verify custom URL/base path, 404 page, search, Mermaid rendering, image loading, and mobile layout.

**Acceptance:** PR checks are green and a commit to the publishing branch updates GitHub Pages successfully.

## Milestone 6 — End-to-end Retail Credit Risk reference project

- [ ] Create synthetic CUSTOMER, LOAN, PAYMENT, DPD, and DEFAULT datasets.
- [ ] Build ingestion and S3 Raw/Cleaned/Curated data layers.
- [ ] Build ETL, catalog, and analytical query workflow.
- [ ] Train a demonstrator PD model and register the model version.
- [ ] Deploy inference and batch scoring paths.
- [ ] Add CI/CD, scheduling, observability, backup, and recovery exercises.
- [ ] Add architecture decision records and end-to-end cost estimate.
- [ ] Verify the complete project from a clean environment.

**Acceptance:** end-to-end flow is reproducible, documented, tested with synthetic data, and has a teardown procedure.

## Cross-cutting definition of done

- [ ] Content is in Vietnamese with standard English technical terminology.
- [ ] Every image has alt text, caption, source/attribution, and reuse permission recorded.
- [ ] Every architecture diagram has an editable source (Mermaid or Draw.io); exported images are not the only source.
- [ ] Every external AWS behavior/pricing claim links to official documentation and is date-checked.
- [ ] Every billable lab lists cleanup commands and possible residual charges.
- [ ] No secrets, real customer data, or non-public banking information are committed.
- [ ] All internal links and the strict documentation build pass.


## UC01 — S3 upload implementation status

- [x] Write Vietnamese lesson covering architecture, 10 WH for S3/IAM/CLI/Boto3/KMS/CloudTrail, alternatives, cost, security and cleanup.
- [x] Add editable Mermaid architecture and trust-boundary diagrams.
- [x] Add synthetic CSV dataset and Boto3 upload/verification scripts.
- [x] Add prefix-scoped IAM policy example.
- [x] Add Terraform private bucket baseline (public access block, ownership controls, versioning, SSE-S3, TLS-only bucket policy).
- [x] Add S3 and IAM service guides.
- [x] Add CI checks for Python compilation, sample CSV tests and IAM JSON validation.
- [ ] Run AWS lab in a dedicated learning account and capture redacted real console screenshots.
- [ ] Verify Terraform plan/apply/destroy in the selected Region.
- [ ] Verify cost and cleanup after execution.
- [ ] Mark UC01 Lab verified only after the above checks pass.
