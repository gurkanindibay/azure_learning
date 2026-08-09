#!/usr/bin/env python3
"""Download Azure Cohort notes from Notion and save as Markdown files."""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

TOKEN_FILE = Path.home() / ".notion-token"
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

# Child pages of Azure Cohort root
CHILD_PAGES = {
    "02-foundations": "1a4058c5-6952-8027-8645-f08fe48b9979",
    "03-relational-operators": "1a4058c5-6952-803a-a5ad-e7325dcfc02a",
    "04-query-optimization-1": "1a4058c5-6952-8005-8488-ef45f6ef0424",
    "05-query-optimization-2": "1a7058c5-6952-8065-a2f3-f0d2674f48ef",
    "06-single-node-qp": "1a7058c5-6952-8085-aa55-ca4aba10a147",
    "07-database-machines": "1a7058c5-6952-80a8-8522-f759b566704e",
    "08-special-topics-governance-event-handling-analytics": "1a7058c5-6952-8075-9303-dcfa56e4ee3f",
    "09-parallel-databases": "1a7058c5-6952-80e1-b886-f4e564e6c98c",
    "10-fabric-sql-query-processing": "1a7058c5-6952-80dd-ad8d-fc3528a1db7a",
    "11-big-data-overview": "1a7058c5-6952-80b2-8ecf-ca2943545ae3",
    "12-machine-learning-and-data-science": "1a7058c5-6952-8059-a5a2-d3dcacd63ca3",
    "13-cloud-tuning": "1a7058c5-6952-8023-a30e-cf0001b5266e",
    "14-introduction-to-concurrency-and-recovery": "1a7058c5-6952-802b-b061-f1825542566e",
    "15-cloud-oltp": "1a7058c5-6952-8019-a199-e029911d5c89",
    "16-distributed-databases": "1a7058c5-6952-8095-80d1-c6bf81921511",
    "17-concurrency-control-in-sql-azure": "1a7058c5-6952-80b9-93bf-c8226fe6a93f",
    "18-recovery-in-sql-azure": "1a7058c5-6952-80c4-a4df-c8cca8519525",
    "19-concurrency-control-and-recovery-in-fabric-sql-part-1": "1a7058c5-6952-800b-9319-de7ea3927505",
    "20-concurrency-control-and-recovery-in-fabric-sql-part-2": "1a7058c5-6952-805b-b82a-ef08af1e47da",
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "unstructured-resources" / "azure-cohort"


_NOTION_TOKEN = None


def notion_request(endpoint, method="GET", data=None):
    """Make a request to the Notion API."""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {_NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  ERROR {e.code}: {body}", file=sys.stderr)
        return None


def fetch_all_blocks(block_id):
    """Fetch all child blocks recursively, handling pagination."""
    all_blocks = []
    cursor = None
    while True:
        url = f"/blocks/{block_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        result = notion_request(url)
        if result is None:
            break
        all_blocks.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    return all_blocks


def rich_text_to_markdown(rich_text_array):
    """Convert Notion rich_text array to markdown string."""
    if not rich_text_array:
        return ""
    parts = []
    for rt in rich_text_array:
        text = rt.get("plain_text", "")
        annotations = rt.get("annotations", {})
        href = rt.get("href")
        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts)


def block_to_markdown(block, depth=0):
    """Convert a single Notion block to markdown."""
    block_type = block.get("type", "")
    has_children = block.get("has_children", False)
    block_id = block.get("id", "")

    if block_type == "paragraph":
        text = rich_text_to_markdown(block["paragraph"]["rich_text"])
        return text + "\n\n" if text else "\n"

    elif block_type == "heading_1":
        text = rich_text_to_markdown(block["heading_1"]["rich_text"])
        return f"# {text}\n\n"

    elif block_type == "heading_2":
        text = rich_text_to_markdown(block["heading_2"]["rich_text"])
        return f"## {text}\n\n"

    elif block_type == "heading_3":
        text = rich_text_to_markdown(block["heading_3"]["rich_text"])
        return f"### {text}\n\n"

    elif block_type == "bulleted_list_item":
        text = rich_text_to_markdown(block["bulleted_list_item"]["rich_text"])
        prefix = "  " * depth
        md = f"{prefix}- {text}\n"
        if has_children:
            children = fetch_all_blocks(block_id)
            for child in children:
                md += block_to_markdown(child, depth + 1)
        return md + "\n"

    elif block_type == "numbered_list_item":
        text = rich_text_to_markdown(block["numbered_list_item"]["rich_text"])
        md = f"1. {text}\n"
        if has_children:
            children = fetch_all_blocks(block_id)
            for child in children:
                md += block_to_markdown(child, depth + 1)
        return md + "\n"

    elif block_type == "to_do":
        text = rich_text_to_markdown(block["to_do"]["rich_text"])
        checked = "x" if block["to_do"].get("checked", False) else " "
        return f"- [{checked}] {text}\n\n"

    elif block_type == "code":
        text = rich_text_to_markdown(block["code"]["rich_text"])
        lang = block["code"].get("language", "")
        return f"```{lang}\n{text}\n```\n\n"

    elif block_type == "quote":
        text = rich_text_to_markdown(block["quote"]["rich_text"])
        return f"> {text}\n\n"

    elif block_type == "callout":
        text = rich_text_to_markdown(block["callout"]["rich_text"])
        icon = block["callout"].get("icon", {}).get("emoji", "")
        return f"> {icon} **Note:** {text}\n\n"

    elif block_type == "divider":
        return "---\n\n"

    elif block_type == "image":
        caption = rich_text_to_markdown(block["image"].get("caption", []))
        url = ""
        if block["image"]["type"] == "external":
            url = block["image"]["external"]["url"]
        elif block["image"]["type"] == "file":
            url = block["image"]["file"]["url"]
        return f"![{caption or 'image'}]({url})\n\n"

    elif block_type == "bookmark":
        url = block["bookmark"]["url"]
        caption = rich_text_to_markdown(block["bookmark"].get("caption", []))
        return f"[{caption or url}]({url})\n\n"

    elif block_type == "table":
        table_md = ""
        rows = fetch_all_blocks(block_id)
        if rows:
            header_row = True
            for row in rows:
                if row["type"] == "table_row":
                    cells = row["table_row"]["cells"]
                    cell_texts = [rich_text_to_markdown(c) for c in cells]
                    table_md += "| " + " | ".join(cell_texts) + " |\n"
                    if header_row:
                        table_md += "| " + " | ".join(["---"] * len(cells)) + " |\n"
                        header_row = False
        return table_md + "\n"

    elif block_type == "equation":
        expr = block["equation"]["expression"]
        return f"$$\n{expr}\n$$\n\n"

    elif block_type == "child_page":
        title = block["child_page"]["title"]
        md = f"\n## {title}\n\n"
        children = fetch_all_blocks(block_id)
        for child in children:
            md += block_to_markdown(child, depth)
        return md

    elif block_type == "child_database":
        title = block["child_database"]["title"]
        return f"🗄️ **Database: {title}**\n\n"

    elif block_type == "link_preview":
        url = block["link_preview"]["url"]
        return f"[{url}]({url})\n\n"

    elif block_type == "synced_block":
        synced_id = block["synced_block"].get("synced_from", {}).get("block_id", block_id)
        if synced_id != block_id:
            children = fetch_all_blocks(synced_id)
            if children:
                md = ""
                for child in children:
                    md += block_to_markdown(child, depth)
                return md
        return ""

    elif block_type == "table_of_contents":
        return "<!-- TOC -->\n\n"

    elif block_type == "link_to_page":
        page_id = block["link_to_page"].get("page_id", "")
        return f"[Linked Page](https://notion.so/{page_id.replace('-', '')})\n\n"

    elif block_type == "embed":
        url = block["embed"]["url"]
        return f"[Embed: {url}]({url})\n\n"

    elif block_type == "video":
        url = ""
        if block["video"]["type"] == "external":
            url = block["video"]["external"]["url"]
        elif block["video"]["type"] == "file":
            url = block["video"]["file"]["url"]
        return f"📹 [Video]({url})\n\n"

    elif block_type == "file":
        url = ""
        if block["file"]["type"] == "external":
            url = block["file"]["external"]["url"]
        elif block["file"]["type"] == "file":
            url = block["file"]["file"]["url"]
        caption = rich_text_to_markdown(block["file"].get("caption", []))
        name = caption or url.split("/")[-1]
        return f"📎 [{name}]({url})\n\n"

    elif block_type == "pdf":
        url = ""
        if block["pdf"]["type"] == "external":
            url = block["pdf"]["external"]["url"]
        elif block["pdf"]["type"] == "file":
            url = block["pdf"]["file"]["url"]
        caption = rich_text_to_markdown(block["pdf"].get("caption", []))
        return f"📄 [PDF: {caption or url}]({url})\n\n"

    elif block_type in ("column_list", "column"):
        if has_children:
            children = fetch_all_blocks(block_id)
            md = ""
            for child in children:
                md += block_to_markdown(child, depth)
            return md
        return ""

    else:
        if has_children:
            children = fetch_all_blocks(block_id)
            md = ""
            for child in children:
                md += block_to_markdown(child, depth)
            return md
        return ""


def process_page(page_id, filename, output_dir):
    """Fetch a Notion page and save as markdown."""
    print(f"  Fetching: {filename}")
    blocks = fetch_all_blocks(page_id)

    md_lines = []
    for block in blocks:
        md_lines.append(block_to_markdown(block))

    content = "".join(md_lines)

    os.makedirs(output_dir, exist_ok=True)
    filepath = output_dir / f"{filename}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    → Saved {filepath} ({len(content)} chars)")
    return filepath


def load_token():
    """Load Notion API token from ~/.notion-token file."""
    if not TOKEN_FILE.exists():
        print(f"ERROR: Token file not found: {TOKEN_FILE}", file=sys.stderr)
        print("Create it with: echo 'ntn_...' > ~/.notion-token", file=sys.stderr)
        sys.exit(1)
    token = TOKEN_FILE.read_text().strip()
    if not token:
        print(f"ERROR: Token file is empty: {TOKEN_FILE}", file=sys.stderr)
        sys.exit(1)
    return token


def main():
    token = load_token()
    # Patch the notion_request closure to use the loaded token
    global _NOTION_TOKEN
    _NOTION_TOKEN = token

    print(f"Downloading Azure Cohort content to: {OUTPUT_DIR}")
    print(f"Total pages: {len(CHILD_PAGES)}")
    print()

    for filename, page_id in CHILD_PAGES.items():
        process_page(page_id, filename, OUTPUT_DIR)

    print(f"\nDone! Files saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
