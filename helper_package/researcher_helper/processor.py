def process_research_text(text: str) -> dict:
    """Generate basic statistics for a research text."""
    if not isinstance(text, str):
        raise TypeError("Research text must be a string.")

    normalized_text = text.strip()
    words = normalized_text.split()

    return {
        "character_count": len(normalized_text),
        "word_count": len(words),
        "processed": True,
    }