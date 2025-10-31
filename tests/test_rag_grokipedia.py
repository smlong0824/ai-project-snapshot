"""Tests for Grokipedia content extraction"""
import pytest
from src.rag.extractors.grokipedia import extract_grokipedia_content

TEST_HTML = """
<html>
<body>
    <h1 class="article-title">Test Article</h1>
    <div class="article-summary">This is a test summary</div>
    <div class="article-content">This is the main content</div>
    <div class="key-concepts">Key concept 1, Key concept 2</div>
    <div class="references">Reference 1, Reference 2</div>
</body>
</html>
"""

def test_extract_grokipedia_content():
    """Test extracting content from Grokipedia HTML"""
    content = extract_grokipedia_content(TEST_HTML)
    
    assert content["title"] == "Test Article"
    assert content["summary"] == "This is a test summary"
    assert content["content"] == "This is the main content"
    assert content["concepts"] == "Key concept 1, Key concept 2"
    assert content["references"] == "Reference 1, Reference 2"

def test_extract_grokipedia_missing_required():
    """Test handling of missing required content"""
    html = """
    <html>
    <body>
        <div class="article-summary">Just a summary</div>
    </body>
    </html>
    """
    
    with pytest.raises(ValueError, match="Missing required content"):
        extract_grokipedia_content(html)