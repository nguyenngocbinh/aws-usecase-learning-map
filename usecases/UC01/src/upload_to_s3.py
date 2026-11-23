"""Upload a local file to S3 using Boto3's default credential chain."""
from __future__ import annotations

import argparse
import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Sequence

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Upload one local file to an S3 landing prefix.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--bucket", default=os.getenv("S3_BUCKET"))
    parser.add_argument("--prefix", default=os.getenv("S3_PREFIX", "landing/loan_demo"))
    parser.add_argument("--region", default=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"))
    parser.add_argument("--key", help="Optional explicit object key")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path: Path = args.file.expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"Input file does not exist: {path}")
    if not args.bucket:
        raise SystemExit("Set --bucket or S3_BUCKET.")
    if not args.region:
        raise SystemExit("Set --region, AWS_REGION, or AWS_DEFAULT_REGION.")

    prefix = args.prefix.strip("/")
    key = args.key or f"{prefix}/{path.name}"
    if key.startswith("/") or ".." in Path(key).parts:
        raise SystemExit("Unsafe object key: use a relative key without '..' segments.")

    checksum = sha256_file(path)
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    client = boto3.Session(region_name=args.region).client("s3")
    try:
        client.upload_file(
            str(path), args.bucket, key,
            ExtraArgs={
                "ServerSideEncryption": "AES256",
                "ContentType": content_type,
                "Metadata": {"sha256": checksum, "source": "aws-usecase-learning-map-uc01"},
            },
        )
        head = client.head_object(Bucket=args.bucket, Key=key)
    except (BotoCoreError, ClientError) as exc:
        raise SystemExit(f"S3 upload/verification failed: {exc}") from exc

    print("Upload verified")
    print(f"Bucket: {args.bucket}")
    print(f"Key: {key}")
    print(f"Size: {head['ContentLength']} bytes")
    print(f"SHA-256 (local metadata): {checksum}")
    print(f"Encryption: {head.get('ServerSideEncryption', 'not reported')}")
    print(f"ETag: {head.get('ETag', 'not reported')} (not assumed to be an MD5 checksum)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
