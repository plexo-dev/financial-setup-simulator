"""Backward-compatible re-exports for the file-based CMS."""

from cms import (
    about_page_context,
    build_about_pitch,
    business_intro,
    parse_context_md,
    pricing_tiers,
    read_context_raw,
    regulatory_disclaimer,
)

__all__ = [
    "about_page_context",
    "build_about_pitch",
    "business_intro",
    "parse_context_md",
    "pricing_tiers",
    "read_context_raw",
    "regulatory_disclaimer",
]
