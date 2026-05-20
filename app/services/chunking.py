import tiktoken

_encoding = tiktoken.get_encoding("cl100k_base")


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> list[str]:
    tokens = _encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(_encoding.decode(chunk_tokens))
        start += chunk_size - overlap
    return chunks


def count_tokens(text: str) -> int:
    return len(_encoding.encode(text))
