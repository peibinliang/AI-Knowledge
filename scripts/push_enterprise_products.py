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
    ("千问办公", ["千问办公", "Qwen Work", "QwenWork"]),
    ("WorkBuddy", ["WorkBuddy", "Work Buddy"]),
    ("腾讯会议 / 腾讯文档", ["腾讯会议", "腾讯文档"]),
    ("WPS / 金山办公", ["WPS", "金山办公"]),
    (
        "Microsoft 365 / Teams / Copilot",
        ["Microsoft 365", "Microsoft Teams", "Teams", "Microsoft Copilot", "Copilot"],
    ),
    ("Google Workspace / Meet", ["Google Workspace", "Google Meet"]),
    ("Slack", ["Slack"]),
    ("Notion", ["Notion"]),
    ("Zoom", ["Zoom"]),
    ("Salesforce / Agentforce", ["Salesforce", "Agentforce"]),
    ("ServiceNow", ["ServiceNow"]),
    ("Atlassian / Jira / Confluence", ["Atlassian", "Jira", "Confluence"]),
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


def find_subsections(
    text: str,
    parent_aliases: list[str],
    child_level: int = 3,
) -> list[tuple[str, str]]:
    """Return child headings and bodies from a structured parent section."""
    parent = find_section(text, parent_aliases)
    if not parent:
        return []

    results: list[tuple[str, str]] = []
    heading = None
    collected: list[str] = []

    for line in parent.splitlines():
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            if level == child_level:
                if heading is not None:
                    body = "\n".join(collected).strip()
                    if body:
                        results.append((heading, body))
                heading = line.lstrip("#").strip()
                collected = []
                continue
            if heading is not None and level < child_level:
                break

        if heading is not None:
            collected.append(line)

    if heading is not None:
        body = "\n".join(collected).strip()
        if body:
            results.append((heading, body))

    return results


def compact_section(section: str, max_chars: int = 1100) -> str:
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


def find_first_section(text: str, aliases_groups: list[list[str]], max_chars: int) -> str:
    for aliases in aliases_groups:
        section = find_section(text, aliases)
        if section:
            return compact_section(section, max_chars)
    return ""


def build_markdown(path: Path, repository: str) -> str:
    text = path.read_text(encoding="utf-8")
    date = path.stem
    github_url = f"https://github.com/{repository}/blob/main/{path.as_posix()}"

    summary = find_first_section(text, [["今日摘要"], ["今日概览"], ["摘要"]], 1900)
    csm = find_first_section(
        text,
        [["CSM 重点关注"], ["CSM关注"], ["客户成功"], ["客户影响"]],
        1600,
    )
    pm = find_first_section(
        text,
        [["项目经理重点关注"], ["项目经理"], ["项目影响"], ["交付影响"]],
        1600,
    )
    actions = find_first_section(
        text,
        [["今日行动建议"], ["今日可跟进"], ["跟进建议"], ["今日最值得关注"]],
        1600,
    )

    parts = [f"# 企业产品资讯快报 {date}"]
    if summary:
        parts.append("## 今日摘要\n" + summary)

    found = 0

    # Preferred format: parse every ### item under the structured product-dynamics section.
    # This keeps the push script compatible with newly tracked enterprise products without
    # requiring every product name to be added to a fixed alias list first.
    product_items = find_subsections(
        text,
        ["今日重点产品动态", "重点产品动态", "产品动态"],
    )
    if product_items:
        for heading, section in product_items:
            found += 1
            parts.append(f"## {heading}\n" + compact_section(section))
    else:
        # Backward compatibility for older briefings that used one product per heading.
        for label, aliases in PRODUCTS:
            section = find_section(text, aliases)
            if not section:
                continue
            found += 1
            parts.append(f"## {label}\n" + compact_section(section))

    other = find_section(text, ["其他企业产品", "其他产品", "同类产品", "其他值得关注"])
    if other:
        parts.append("## 其他值得关注的企业产品\n" + compact_section(other, 1400))

    if csm:
        parts.append("## CSM 重点关注\n" + csm)
    if pm:
        parts.append("## 项目经理重点关注\n" + pm)
    if actions:
        parts.append("## 今日可跟进行动\n" + actions)

    if found == 0 and not other:
        raise RuntimeError(
            "No supported enterprise product sections found. Expected a structured "
            "'今日重点产品动态' section with ### product items, supported product headings, "
            "or an '其他企业产品' section."
        )

    parts.append(f"[查看 GitHub 完整企业产品资讯]({github_url})")
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
    webhook = (
        os.environ.get("ENTERPRISE_DINGTALK_WEBHOOK", "").strip()
        or os.environ.get("DINGTALK_WEBHOOK", "").strip()
    )
    secret = (
        os.environ.get("ENTERPRISE_DINGTALK_SECRET", "").strip()
        or os.environ.get("DINGTALK_SECRET", "").strip()
        or None
    )
    briefing_path = os.environ.get("BRIEFING_PATH", "").strip()
    repository = os.environ.get("GITHUB_REPOSITORY", "peibinliang/AI-Knowledge").strip()

    if not webhook:
        print(
            "ENTERPRISE_DINGTALK_WEBHOOK / DINGTALK_WEBHOOK secret is not configured.",
            file=sys.stderr,
        )
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
    base_title = f"企业产品资讯快报 {path.stem}"

    for index, chunk in enumerate(chunks, start=1):
        title = base_title if len(chunks) == 1 else f"{base_title} ({index}/{len(chunks)})"
        if len(chunks) > 1:
            chunk = f"# {title}\n\n" + re.sub(r"^# .*?\n\n", "", chunk, count=1)
        post_markdown(webhook, secret, title, chunk)
        print(f"Sent enterprise product briefing {index}/{len(chunks)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())