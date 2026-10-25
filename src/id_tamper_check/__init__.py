"""Explainable SSIM-based tampering visualization for ID document images."""

from .core import ComparisonResult, Region, compare_documents, compare_images, load_image, save_result

__all__ = [
    "ComparisonResult",
    "Region",
    "compare_documents",
    "compare_images",
    "load_image",
    "save_result",
]
__version__ = "0.2.0"
