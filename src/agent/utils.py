"""
Shared utilities for the Airtel B2B AI Sales Assistant Agent.
"""


def _build_context(chunks: list[dict]) -> tuple[str, list[str]]:
    """
    Build a formatted context string and deduplicated source URL list from retrieved chunks.

    Args:
        chunks: List of chunk dicts, each containing 'text' and optionally 'source_url'.

    Returns:
        A tuple of (formatted_context_string, list_of_unique_source_urls).
    """
    if not chunks:
        return "", []

    context_parts: list[str] = []
    seen_urls: list[str] = []
    for c in chunks:
        url = c.get("source_url", "")
        context_parts.append(
            f"[Source: {url}]\n{c['text']}"
        )
        if url and url not in seen_urls:
            seen_urls.append(url)

    return "\n\n---\n\n".join(context_parts), seen_urls

