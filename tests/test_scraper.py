"""Test the technical documentation scraper"""
import pytest
from pathlib import Path
from src.rag.scraper import TechDocScraper
from src.rag.runner import ScrapingRunner

@pytest.fixture
def config():
    return {
        "chunk_size": 512,
        "chunk_overlap": 50,
        "delay": 0.1,  # Faster for tests
        "rag_config": {
            "embedding_model": "sentence-transformers/all-mpnet-base-v2",
            "collection_name": "test_technical_docs"
        },
        "rag_index_dir": Path.home() / "Nova/data/rag_index"
    }

@pytest.fixture
def scraper(config):
    return TechDocScraper(config)

def test_can_fetch(scraper):
    # Should be allowed
    assert scraper.can_fetch("https://pytorch.org/docs/")
    # Should respect robots.txt
    assert not scraper.can_fetch("https://pytorch.org/admin/")

def test_detect_content_type(scraper):
    test_doc = {
        "success": True,
        "content": "This is a PyTorch tutorial about neural networks",
        "metadata": {
            "title": "PyTorch Neural Networks Guide"
        }
    }
    tags = scraper.detect_content_type("https://pytorch.org/docs/stable/nn.html", test_doc)
    assert "pytorch" in tags
    assert "machine_learning" in tags

def test_fetch_url(scraper):
    # Test with a reliable documentation page
    result = scraper.fetch_url("https://pytorch.org/docs/stable/nn.html")
    assert result is not None
    assert result["success"] is True
    assert "content" in result
    assert "metadata" in result
    assert "url" in result["metadata"]
    assert "title" in result["metadata"]
    
async def test_scrape_subject(scraper):
    results = await scraper.scrape_subject(
        "test",
        ["https://pytorch.org/docs/stable/nn.html"],
        max_pages=1
    )
    assert len(results) == 1
    assert results[0]["success"] is True
    assert "pytorch" in results[0]["metadata"]["tags"]