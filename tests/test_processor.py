
from research_helper import process_research_text


def test_process_research_text_counts_words_and_characters():
    result = process_research_text("Research security testing")

    assert result["character_count"] == 25
    assert result["word_count"] == 3
    assert result["processed"] is True
