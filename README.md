# AWS Use Case Learning Map

A hands-on AWS learning portal covering Data Platform, Machine Learning, DevOps, Operations, and Security & Governance.

> **Learning by building:** architecture first, service selection, practical labs, repeatable infrastructure, testing, operations, and cost-aware cleanup.

## Learning domains

| Domain | Use cases | Focus |
|---|---:|---|
| A. Data Platform | UC01–UC03 | Upload, Data Lake & ETL, database migration |
| B. Machine Learning | UC04–UC06 | Model training, inference API, batch scoring |
| C. DevOps | UC07–UC09 | GitHub, GitLab, CI/CD |
| D. Operations | UC10–UC11 | Scheduling, monitoring, incident response |
| E. Security & Governance | UC12 | IAM, encryption, backup, disaster recovery |

## Documentation website

The documentation is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and published using GitHub Pages + GitHub Actions.

After enabling **Settings → Pages → Build and deployment → GitHub Actions** and merging the site workflow, the site will be available at:

`https://nguyenngocbinh.github.io/aws-usecase-learning-map/`

## Repository layout

- `docs/`: learning portal content (Markdown, Mermaid, referenced diagrams and screenshots).
- `usecases/`: executable lab code and per-use-case assets.
- `infrastructure/`: reusable Terraform and deployment components.
- `.github/workflows/`: documentation deployment and code quality workflows.
- `PROJECT_TODOS.md`: implementation backlog and acceptance criteria.

## Local preview

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-docs.txt
mkdocs serve
```

Open http://127.0.0.1:8000.

Validate a production build:

```powershell
mkdocs build --strict
```

## Safety and cost principles

1. Never commit AWS access keys, credentials, customer data, or production secrets.
2. Use synthetic datasets in labs.
3. Prefer short-lived credentials and GitHub OIDC roles over long-lived access keys.
4. Document estimated cost, region assumptions, cleanup, and resource deletion for every billable lab.
5. Deploy to an isolated learning account; do not reuse bank or production environments.

## Learning standard

Every AWS service page must answer the 10 WH questions: What, Why, When, Where, Who, Which, How, How much, What if, and How compared. Every use case must include architecture, alternatives, hands-on steps, code, validation, troubleshooting, security, cost, cleanup, and knowledge checks.
