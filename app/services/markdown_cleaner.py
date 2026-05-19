import re


def clean_markdown(text: str) -> str:
    """
    Light cleaning that preserves semantic content for embedding.
    Removes only structural noise, keeps prose and code content.
    """
    # Remove complete fenced code blocks (opening + closing markers only)
    # Keep the code content itself — it carries semantic meaning
    text = re.sub(r"```[\w-]*\n", "", text)  # opening fence
    text = re.sub(r"\n```", "\n", text)  # closing fence

    # Remove MkDocs admonition markers (/// type \n ... ///)
    # FastAPI docs use: /// note | warning | tip etc.
    text = re.sub(r"^///\s*\w+.*?$", "", text, flags=re.MULTILINE)

    # Remove HTML tags (div, details, summary, etc.) but keep inner text
    text = re.sub(r"<[^>]+>", "", text)

    # Remove inline code backticks but keep content
    text = re.sub(r"`([^`\n]*)`", r"\1", text)

    # Remove markdown images entirely (no semantic value)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # Convert markdown links to anchor text only
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove heading markers but KEEP heading text (critical for semantics)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove MkDocs anchor IDs like { #deploy-your-app }
    text = re.sub(r"\{\s*#[\w-]+\s*\}", "", text)

    # Remove blockquote markers
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Normalize whitespace — collapse spaces/tabs but preserve newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
