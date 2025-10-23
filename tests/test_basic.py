"""
Test base per Officina AI Assistant
"""
import pytest
from pathlib import Path


def test_imports():
    """Test che tutti i moduli si importino correttamente"""
    from config import settings
    from src import ManualProcessor, VectorStoreManager, OfficinaChatbot
    
    assert settings is not None
    assert ManualProcessor is not None
    assert VectorStoreManager is not None
    assert OfficinaChatbot is not None


def test_config():
    """Test configurazione"""
    from config import settings
    
    assert settings.CHUNK_SIZE > 0
    assert settings.CHUNK_OVERLAP >= 0
    assert settings.RETRIEVAL_K > 0


def test_manual_processor():
    """Test processor manuali"""
    from src import ManualProcessor
    
    processor = ManualProcessor()
    
    # Test estrazione metadata
    metadata = processor.extract_metadata_from_filename("FIAT_500_2020_Manuale.pdf")
    assert metadata["marca"] == "FIAT"
    assert metadata["modello"] == "500"
    assert metadata["anno"] == "2020"


def test_utils():
    """Test utility functions"""
    from src.utils import format_file_size, extract_car_info
    
    # Test format_file_size
    assert format_file_size(1024) == "1.00 KB"
    assert format_file_size(1024 * 1024) == "1.00 MB"
    
    # Test extract_car_info
    info = extract_car_info("FIAT 500 2020")
    assert info["marca"] == "FIAT"
    assert info["anno"] == "2020"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])