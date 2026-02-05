"""Simple AI social media automation starter.

Usage examples:
  python social_automation.py generate --topic "AI marketing" --brand "MyBrand"
  python social_automation.py post --input output/latest_post.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


@dataclass
class PostPayload:
    topic: str
    platform: str
    brand: str
    caption: str
    hashtags: list[str]
    image_prompt: str
    image_path: str
    created_at: str


def get_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def generate_copy(client, topic: str, brand: str, platform: str) -> dict[str, Any]:
    prompt = (
        "Create a social media post package as strict JSON with keys: "
        "caption, hashtags, image_prompt. "
        f"Topic: {topic}. Brand voice: {brand}. Platform: {platform}. "
        "Caption should be concise and engaging. "
        "hashtags should be an array of 8-12 relevant tags without '#'. "
        "image_prompt should describe a photorealistic social media hero image."
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.8,
    )

    raw_text = response.output_text.strip()
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model output was not valid JSON: {raw_text}") from exc

    required_keys = {"caption", "hashtags", "image_prompt"}
    if not required_keys.issubset(data):
        raise ValueError(f"Missing keys in generated JSON. Got: {list(data.keys())}")
    if not isinstance(data["hashtags"], list):
        raise ValueError("hashtags must be a JSON array")

    return data


def generate_image(client, image_prompt: str, topic_slug: str) -> str:
    image_result = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt,
        size="1024x1024",
    )

    image_bytes = image_result.data[0].b64_json
    image_path = OUTPUT_DIR / f"{topic_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image_path.write_bytes(__import__("base64").b64decode(image_bytes))
    return str(image_path)


def save_payload(payload: PostPayload) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"post_{timestamp}.json"
    json_path.write_text(json.dumps(asdict(payload), indent=2), encoding="utf-8")

    latest_path = OUTPUT_DIR / "latest_post.json"
    latest_path.write_text(json.dumps(asdict(payload), indent=2), encoding="utf-8")
    return json_path


def publish_to_platform(payload: PostPayload, dry_run: bool = True) -> None:
    # Replace this stub with real integrations.
    # Example: Instagram Graph API / X API / LinkedIn API.
    platform_log = OUTPUT_DIR / "publish_log.jsonl"
    event = {
        "status": "dry_run" if dry_run else "published",
        "platform": payload.platform,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caption": payload.caption,
        "hashtags": payload.hashtags,
        "image_path": payload.image_path,
    }
    with platform_log.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")


def slugify(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in text).strip("-")[:40]


def cmd_generate(args: argparse.Namespace) -> None:
    client = get_client()
    generated = generate_copy(client, args.topic, args.brand, args.platform)
    image_path = generate_image(client, generated["image_prompt"], slugify(args.topic))

    payload = PostPayload(
        topic=args.topic,
        platform=args.platform,
        brand=args.brand,
        caption=generated["caption"],
        hashtags=[str(tag).lstrip("#") for tag in generated["hashtags"]],
        image_prompt=generated["image_prompt"],
        image_path=image_path,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    output_file = save_payload(payload)
    print(f"Generated post package: {output_file}")
    print(f"Image saved at: {image_path}")


def cmd_post(args: argparse.Namespace) -> None:
    payload_data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    payload = PostPayload(**payload_data)
    publish_to_platform(payload, dry_run=args.dry_run)
    print(f"Post event recorded for platform={payload.platform}, dry_run={args.dry_run}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI social media automation starter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate caption, hashtags, and image")
    generate.add_argument("--topic", required=True, help="Post topic")
    generate.add_argument("--brand", required=True, help="Brand voice or company name")
    generate.add_argument("--platform", default="instagram", help="Target platform")
    generate.set_defaults(func=cmd_generate)

    post = subparsers.add_parser("post", help="Publish or dry-run a generated payload")
    post.add_argument("--input", required=True, help="Path to JSON payload")
    post.add_argument("--dry-run", action="store_true", help="Log only, do not publish")
    post.set_defaults(func=cmd_post)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
