"""Explainable SSIM-based tampering visualization for ID document images."""

from .align import AlignmentError, align_to_reference
from .core import ComparisonResult, Region, compare_documents, compare_images, load_image, save_result

__all__ = [
    "AlignmentError",
    "ComparisonResult",
    "Region",
    "align_to_reference",
    "compare_documents",
    "compare_images",
    "load_image",
    "save_result",
]
__version__ = "0.2.0"
