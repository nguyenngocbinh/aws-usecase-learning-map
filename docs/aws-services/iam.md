# AWS Identity and Access Management (IAM)

<small>SECURITY · IDENTITY · UC01</small>

## What

IAM controls authentication and authorization for AWS resources. A request is evaluated using the principal's identity policies, resource policies and applicable organization/session controls.

## 10 WH questions

| WH | Answer |
|---|---|
| What | AWS service for identities, roles, policies, federation and permission evaluation. |
| Why | Enforce least privilege, separate duties, scope access and audit authorization. |
| When | Every human, application, automation and service-to-service access path. |
| Where | IAM is global; policies apply to requests against regional/global resources. |
| Who | IAM users/roles, federated identities, AWS service principals and external principals. |
| Which | Prefer IAM Identity Center/federation and temporary role sessions over long-lived user keys. |
| How | Trust policy defines who can assume a role; permissions policy defines allowed actions/resources/conditions. |
| How much | Core IAM capabilities generally have no separate per-policy charge; review related identity/security service pricing. |
| What if | Diagnose explicit deny, missing action, wrong resource ARN, trust failure, SCP, permission boundary, session policy or KMS key policy. |
| How compared | Role/federation provides temporary credentials; IAM user access keys are long-lived and require lifecycle management. |

## Example: prefix-scoped S3 upload permissions

The UC01 policy grants:
- s3:ListBucket only for the landing/loan_demo prefix.
- s3:PutObject and multipart upload permissions only under landing/loan_demo/*.
- s3:GetObject only for that prefix to support head-object verification.

It deliberately does not grant bucket administration, public access, delete, or access to other prefixes.

## Policy evaluation checklist

1. Confirm caller identity with sts:GetCallerIdentity.
2. Confirm the role trust policy permits the expected identity/provider.
3. Inspect identity-based policies.
4. Inspect bucket/resource policy and explicit denies.
5. Inspect Organizations SCP and permissions boundary.
6. For SSE-KMS, inspect KMS key policy and grants.
7. Use IAM Access Analyzer and policy simulator as appropriate.

## Official references

- [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [IAM policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
- [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
- [IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
