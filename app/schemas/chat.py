"""
Chat API schemas for Risk SME Agent.
"""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language question about risks",
        examples=["Show me all critical risks in Infrastructure domain"],
    )
    model: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="AI model to use for code generation",
    )
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Temperature for AI generation (0.0-1.0)",
    )
    show_code: bool = Field(
        default=False,
        description="Include generated code in response",
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    answer: str = Field(
        ...,
        description="Natural language answer to the question",
    )
    status: str = Field(
        ...,
        description="Query status: success, no_results, invalid_request, or error",
    )
    answer_rows: list[dict[str, Any]] | None = Field(
        default=None,
        description="Structured data results (if applicable)",
    )
    code: str | None = Field(
        default=None,
        description="Generated SQLAlchemy code (if show_code=True)",
    )
    error: str | None = Field(
        default=None,
        description="Error message (if status=error)",
    )
    execution_log: str | None = Field(
        default=None,
        description="Execution logs from code run",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "I found 12 active risks in the system. These span multiple technology domains and risk categories.",
                "status": "success",
                "answer_rows": [
                    {
                        "risk_id": "TR-2025-001",
                        "title": "Enterprise Data Loss Event",
                        "category": "Data Management",
                        "status": "Active",
                        "exposure": "Critical (15)",
                    }
                ],
                "code": None,
                "error": None,
                "execution_log": "LOG: Found 12 active risks. STATUS=success",
            }
        }
