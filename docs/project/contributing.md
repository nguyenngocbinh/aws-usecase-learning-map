# Contributing

## Content standards

- Vietnamese explanations with official English service names.
- Use case pages follow a practical implementation structure: Business Scenario, Objectives, Architecture, Scope/Service Selection, Prerequisites, Hands-on Steps, Validation, Troubleshooting, Security, Cost, Cleanup, and Knowledge Check.
- Do not add WH-question sections to use case pages. Reserve the 10-question WH framework for AWS knowledge/service concept pages.
- Use Mermaid for editable flow diagrams and Draw.io for detailed AWS architecture diagrams.
- Every external visual must have reuse permission and attribution recorded in the asset register.
- Link claims about service behavior to official AWS documentation.

## Code standards

- Never commit credentials, real personal/customer data, account IDs, internal endpoints, or production configurations.
- Keep lab resources tagged (for example, `Project=aws-usecase-learning-map`, `UseCase=UCxx`, `Environment=learning`).
- Provide safe defaults, error handling, validation, and cleanup instructions.
- Document required IAM permissions and why they are needed.

## Pull request checklist

- [ ] Docs build with `mkdocs build --strict`.
- [ ] Internal links and images work.
- [ ] Code checks/tests pass.
- [ ] Costs, security implications, and cleanup are documented.
- [ ] Diagrams have editable sources and image attribution.
