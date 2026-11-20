# UC01 — Visual assets and diagram guide

## Visuals included

The UC01 lesson uses editable Mermaid diagrams for:
1. Local/on-prem file → CLI/Boto3 → IAM → private S3 bucket.
2. Identity trust boundary and prefix-scoped permissions.
3. Recommended landing-prefix layout.

Mermaid diagrams render as vector graphics in the documentation site, and their source remains editable in Markdown.

## Official AWS visual resources

- [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) — official icon downloads and usage guidance.
- [AWS Architecture Center](https://aws.amazon.com/architecture/) — architecture reference material.
- [Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) — service concepts and diagrams.
- [AWS IAM documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) — identity and policy concepts.

Do not copy images from random blogs/search results. Record source URL, creator/provider, license/terms, retrieval date and attribution in the asset register.

## Real screenshot capture checklist

Capture these only after executing the lab in the actual learning account:
- S3 bucket settings: Region, Block Public Access, Object Ownership.
- Versioning and default encryption.
- Successful upload and object properties.
- CLI head-object output with sensitive account details redacted.
- Terraform plan/apply output with account identifiers redacted.

Never fabricate console screenshots or represent a conceptual diagram as proof of a real deployment.
