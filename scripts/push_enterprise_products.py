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

MAX_MESSAGE_CHARS = 11000
PRODUCTS = [
    ("钉钉", ["钉钉", "DingTalk"]),
    ("飞书", ["飞书", "Feishu", "Lark"]),
    ("企业微信", ["企业微信", "WeCom"]),
    ("TRAE Work", ["TRAE Work", "Trae Work"]),
    ("千问办公", ["千问办公", "QwenWork", "Qwen Work"]),
    ("WorkBuddy", ["WorkBuddy", "Work Buddy"]),
]


def find_section(text: str, aliases: list[str]) -> str:
    lines = text.splitlines()
    start = None
    level = None
    for i, line in enumerate(lines):
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip()
        if any(alias.lower() in heading.lower() for alias in aliases):
            start = i + 1
            level = len(line) - len(line.lstrip("#"))
            break
    if start is None:
        return ""

    collected = []
    for line in lines[start:]:
        if line.startswith("#"):
            current_level = len(line) - len(line.lstrip("#"))
            if current_level <= level:
                break
        collected.append(line)
    return "\n".join(collected).strip()


def compact_section(section: str, max_chars: int = 1400) -> str:
    if not section:
        return ""
    section = re.sub(r"\n{3,}", "\n\n", section).strip()
    if len(section) <= max_chars:
        return section

    blocks = [b.strip() for b in section.split("\n\n") if b.strip()]
    chosen = []
    total = 0
    for block in blocks:
        if total + len(block) + 2 > max_chars:
            break
        chosen.append(block)
        total += len(block) + 2
    result = "\n\n".join(chosen).strip()
    return result if result else section[:max_chars].rstrip() + "…"


def extract_summary(text: str) -> str:
    for aliases in (["今日摘要"], ["今日概览"], ["摘要"]):
        section = find_section(text, aliases)
        if section:
            return compact_section(section, 2200)
    return ""


def extract_actions(text: str) -> str:
    for aliases in (["今日最值得关注"], ["今日行动"], ["行动建议"], ["持续观察"]):
        section = find_section(text, aliases)
        if section:
            return compact_section(section, 1800)
    return ""


def build_markdown(path: Path, repository: str) -> str:
    text = path.read_text(encoding="utf-8")
    date = path.stem
    github_url = f"https://github.com/{repository}/blob/main/{path.as_posix()}"

    parts = [f"# 企业 AI 办公产品情报 {date}"]
    summary = extract_summary(text)
    if summary:
        parts.append("## 今日摘要\n" + summary)

    found = 0
    for label, aliases in PRODUCTS:
        section = find_section(text, aliases)
        if not section:
            continue
        found += 1
        parts.append(f"## {label}\n" + compact_section(section))

    # Allow an 'other enterprise products' section without forcing a fixed vendor list.
    other = find_section(text, ["其他企业产品", "其他产品", "同类产品"])
    if other:
        parts.append("## 其他值得关注的企业产品\n" + compact_section(other, 1800))

    actions = extract_actions(text)
    if actions:
        parts.append("## 今日最值得关注 / 行动建议\n" + actions)

    if found == 0 and not other:
        raise RuntimeError(
            "No supported enterprise product sections found. Expected headings for DingTalk, "
            "Feishu/Lark, WeCom, TRAE Work, QwenWork, WorkBuddy, or other enterprise products."
        )

    parts.append(f"[查看 GitHub 完整企业产品情报]({github_url})")
    return "\n\n".join(parts)


def split_markdown(text: str, limit: int = MAX_MESSAGE_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    current = []
    size = 0
    for block in text.split("\n\n"):
        block_size = len(block) + 2
        if current and size + block_size > limit:
            chunks.append("\n\n".join(current))
            current = [block]
            size = len(block)
        else:
            current.append(block)
            size += block_size
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
        print(f"Enterprise product briefing does not exist: {path}", file=sys.stderr)
        return 2

    markdown = build_markdown(path, repository)
    chunks = split_markdown(markdown)
    base_title = f"企业 AI 办公产品情报 {path.stem}"

    for index, chunk in enumerate(chunks, start=1):
        title = base_title if len(chunks) == 1 else f"{base_title} ({index}/{len(chunks)})"
        if len(chunks) > 1:
            chunk = f"# {title}\n\n" + re.sub(r"^# .*?\n\n", "", chunk, count=1)
        post_markdown(webhook, secret, title, chunk)
        print(f"Sent enterprise product briefing {index}/{len(chunks)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
