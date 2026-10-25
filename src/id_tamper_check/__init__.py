"""Explainable SSIM-based tampering visualization for ID document images."""

from .core import ComparisonResult, compare_documents, save_result

__all__ = ["ComparisonResult", "compare_documents", "save_result"]
__version__ = "0.2.0"
