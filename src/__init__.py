"""
Officina AI Assistant - Source modules
"""

from .document_processor import ManualProcessor
from .vectorstore import VectorStoreManager
from .qa_chain import OfficinaChatbot, SimpleChatbot
from .utils import (
    setup_logging,
    validate_pdf_file,
    get_available_brands,
    get_available_models,
    check_system_requirements
)

__all__ = [
    "ManualProcessor",
    "VectorStoreManager",
    "OfficinaChatbot",
    "SimpleChatbot",
    "setup_logging",
    "validate_pdf_file",
    "get_available_brands",
    "get_available_models",
    "check_system_requirements"
]