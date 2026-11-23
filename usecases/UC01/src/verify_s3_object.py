"""Verify metadata for the uploaded UC01 sample object."""
from __future__ import annotations

import os
import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def main() -> int:
    bucket = os.getenv("S3_BUCKET")
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    prefix = os.getenv("S3_PREFIX", "landing/loan_demo").strip("/")
    key = os.getenv("S3_KEY", f"{prefix}/sample_loans.csv")
    if not bucket or not region:
        print("Set S3_BUCKET and AWS_REGION.", file=sys.stderr)
        return 2

    client = boto3.Session(region_name=region).client("s3")
    try:
        head = client.head_object(Bucket=bucket, Key=key)
    except (BotoCoreError, ClientError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1

    print(f"s3://{bucket}/{key}")
    print(f"ContentLength={head['ContentLength']}")
    print(f"ContentType={head.get('ContentType')}")
    print(f"ServerSideEncryption={head.get('ServerSideEncryption')}")
    print(f"VersionId={head.get('VersionId')}")
    print(f"Metadata={head.get('Metadata', {})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
