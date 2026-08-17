import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib import parse, request


MAX_MESSAGE_CHARS = 12000


def extract_section(text: str, heading_pattern: str) -> str:
    lines = text.splitlines()
    start = None
    collected = []
    pattern = re.compile(heading_pattern)
    for index, line in enumerate(lines):
        if pattern.search(line):
            start = index + 1
            break
    if start is None:
        return ""
    for line in lines[start:]:
        if line.startswith("#") and collected:
            break
        if line.strip() == "---" and collected:
            break
        collected.append(line)
    return "\n".join(collected).strip()


def extract_section_highlights(text: str) -> list[str]:
    sections = [
        ("🇨🇳 中国 AI", ["中国 AI", "中国AI"]),
        ("🌍 全球 AI / Agent", ["全球 AI", "全球AI"]),
        ("🏢 中国重点科技企业", ["中国重点科技企业", "重点科技企业"]),
        ("📱 全球 3C", ["全球 3C", "全球3C", "消费电子"]),
        ("⭐ GitHub AI 项目", ["GitHub AI", "GitHub"]),
    ]
    lines = text.splitlines()
    result = []

    for label, keywords in sections:
        start = None
        for i, line in enumerate(lines):
            if line.startswith("# ") and any(keyword in line for keyword in keywords):
                start = i + 1
                break
        if start is None:
            continue

        headings = []
        for line in lines[start:]:
            if line.startswith("# "):
                break
            if line.startswith("## "):
                title = re.sub(r"^##\s+", "", line).strip()
                title = re.sub(r"^\d+[\.、]\s*", "", title)
                if title and title not in headings:
                    headings.append(title)
                if len(headings) >= 3:
                    break
        if headings:
            result.append(f"### {label}\n" + "\n".join(f"- {item}" for item in headings))

    return result


def build_markdown(path: Path, repository: str) -> str:
    text = path.read_text(encoding="utf-8")
    date = path.stem
    github_url = f"https://github.com/{repository}/blob/main/{path.as_posix()}"

    summary = extract_section(text, r"^##\s+今日摘要")
    if not summary:
        summary = extract_section(text, r"^#\s+今日摘要")

    actions = extract_section(text, r"今日最值得行动|今日行动")
    highlights = extract_section_highlights(text)

    parts = [f"# AI 科技每日简报 {date}"]
    if summary:
        parts.append("## 今日摘要\n" + summary)
    if highlights:
        parts.append("## 五大栏目重点\n" + "\n\n".join(highlights))
    if actions:
        parts.append("## 今日最值得行动 / 持续观察\n" + actions)
    parts.append(f"[查看 GitHub 完整简报]({github_url})")
    return "\n\n".join(parts)


def split_markdown(text: str, limit: int = MAX_MESSAGE_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks = []
    current = []
    current_len = 0
    for block in text.split("\n\n"):
        size = len(block) + 2
        if current and current_len + size > limit:
            chunks.append("\n\n".join(current))
            current = [block]
            current_len = len(block)
        else:
            current.append(block)
            current_len += size
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def signed_webhook(webhook: str, secret: str | None) -> str:
    if not secret:
        return webhook
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), string_to_sign, digestmod=hashlib.sha256).digest()
    sign = parse.quote_plus(base64.b64encode(digest).decode("utf-8"))
    separator = "&" if "?" in webhook else "?"
    return f"{webhook}{separator}timestamp={timestamp}&sign={sign}"


def post_markdown(webhook: str, secret: str | None, title: str, markdown: str) -> None:
    payload = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": markdown},
        "at": {"atMobiles": [], "isAtAll": False},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        signed_webhook(webhook, secret),
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        raw = response.read().decode("utf-8")
    result = json.loads(raw)
    if result.get("errcode") != 0:
        raise RuntimeError(f"DingTalk returned error: {result}")


def main() -> int:
    webhook = os.environ.get("DINGTALK_WEBHOOK", "").strip()
    secret = os.environ.get("DINGTALK_SECRET", "").strip() or None
    briefing_path = os.environ.get("BRIEFING_PATH", "").strip()
    repository = os.environ.get("GITHUB_REPOSITORY", "peibinliang/AI-Knowledge").strip()

    if not webhook:
        print("DINGTALK_WEBHOOK secret is not configured.", file=sys.stderr)
        return 2
    if not briefing_path:
        print("BRIEFING_PATH is empty.", file=sys.stderr)
        return 2

    path = Path(briefing_path)
    if not path.is_file():
        print(f"Briefing file does not exist: {path}", file=sys.stderr)
        return 2

    markdown = build_markdown(path, repository)
    chunks = split_markdown(markdown)
    base_title = f"AI 科技每日简报 {path.stem}"

    for index, chunk in enumerate(chunks, start=1):
        if len(chunks) > 1:
            title = f"{base_title} ({index}/{len(chunks)})"
            chunk = f"# {title}\n\n" + re.sub(r"^# .*?\n\n", "", chunk, count=1)
        else:
            title = base_title
        post_markdown(webhook, secret, title, chunk)
        print(f"Sent DingTalk message {index}/{len(chunks)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
