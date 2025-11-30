"""
Risk SME (Subject Matter Expert) Agent

A chat-based AI agent for querying the Technology Risk Register database.
"""

from .risk_sme_agent import execute_generated_code, generate_llm_code, risk_sme_agent
from .risk_utils import (
    build_schema_block,
    format_risk_for_display,
    get_dropdown_values,
    get_sample_risks,
)

__version__ = "0.1.0"

__all__ = [
    "risk_sme_agent",
    "generate_llm_code",
    "execute_generated_code",
    "build_schema_block",
    "get_sample_risks",
    "get_dropdown_values",
    "format_risk_for_display",
]
