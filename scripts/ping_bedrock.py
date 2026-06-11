#!/usr/bin/env python3
"""Ping Amazon Bedrock to confirm access to a Claude model (default: Sonnet 4.6).

Usage:
    AWS_PROFILE=Loka-ml uv run scripts/ping_bedrock.py
    uv run scripts/ping_bedrock.py --profile Loka-ml --region us-east-1
    uv run scripts/ping_bedrock.py --model us.anthropic.claude-sonnet-4-6
"""

from __future__ import annotations

import argparse
import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Bedrock model IDs carry an `anthropic.` provider prefix. Newer Claude models are
# typically only reachable via a cross-region inference profile (the `us.` prefix).
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-6"
DEFAULT_REGION = "us-east-1"
DEFAULT_PROFILE = "Loka-ml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="AWS profile name")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Bedrock model id / inference profile")
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    client = session.client("bedrock-runtime")

    print(f"Pinging {args.model} via profile={args.profile} region={args.region} ...")
    try:
        response = client.converse(
            modelId=args.model,
            messages=[{"role": "user", "content": [{"text": "Reply with exactly: pong"}]}],
            inferenceConfig={"maxTokens": 16, "temperature": 0.0},
        )
    except ClientError as err:
        code = err.response.get("Error", {}).get("Code", "Unknown")
        msg = err.response.get("Error", {}).get("Message", str(err))
        print(f"FAILED [{code}]: {msg}", file=sys.stderr)
        return 1
    except BotoCoreError as err:
        print(f"FAILED: {err}", file=sys.stderr)
        return 1

    text = "".join(
        block.get("text", "")
        for block in response["output"]["message"]["content"]
    ).strip()
    usage = response.get("usage", {})
    print(f"OK — model replied: {text!r}")
    print(f"tokens: in={usage.get('inputTokens')} out={usage.get('outputTokens')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
