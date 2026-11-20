# UC01 — S3 Upload Lab

Runnable sample for the UC01 learning page.

- data/sample_loans.csv: synthetic, non-customer sample rows.
- src/upload_to_s3.py: Boto3 upload using the default credential chain.
- src/verify_s3_object.py: verify object metadata and encryption.
- iam/uc01-upload-policy.json: prefix-scoped identity policy template.
- infrastructure/terraform/: private S3 bucket baseline.
- requirements.txt: Python dependency.

## Quick start (PowerShell)

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r usecases/UC01/requirements.txt
aws sso login --profile aws-learning
$env:AWS_PROFILE = "aws-learning"
$env:AWS_REGION = "ap-southeast-1"
$env:S3_BUCKET = "your-unique-bucket-name"
python usecases/UC01/src/upload_to_s3.py usecases/UC01/data/sample_loans.csv
python usecases/UC01/src/verify_s3_object.py
~~~

Never commit credentials, real banking data, .env files or Terraform state.
