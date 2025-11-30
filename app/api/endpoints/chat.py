"""
Chat API endpoint for Risk SME Agent.

Provides natural language query interface to the Risk Register database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.risk_sme.risk_sme_agent import risk_sme_agent
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """
    Chat with the Risk SME Agent using natural language.

    The agent generates SQLAlchemy code to query the risk database
    and returns both natural language answers and structured data.

    Args:
        request: ChatRequest containing the question and optional parameters
        db: Database session dependency

    Returns:
        ChatResponse with answer, status, and optional structured data

    Raises:
        HTTPException: If the question is invalid or execution fails

    Examples:
        ```python
        # Simple query
        POST /api/v1/chat
        {
            "question": "Show me all critical risks"
        }

        # With code visibility
        POST /api/v1/chat
        {
            "question": "How many risks does each owner have?",
            "show_code": true
        }
        ```
    """
    # Validate question
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    try:
        # Call the risk SME agent
        result = risk_sme_agent(
            question=request.question,
            session=db,
            model=request.model,
            temperature=request.temperature,
        )

        # Extract execution results
        exec_result = result.get("exec", {})
        answer = exec_result.get("answer", "No answer generated")
        status = exec_result.get("status", "error")
        answer_rows = exec_result.get("answer_rows")
        code = exec_result.get("code") if request.show_code else None
        error = exec_result.get("error")
        execution_log = exec_result.get("stdout")

        # If there's an error, include it in the response
        if error:
            return ChatResponse(
                answer="An error occurred while processing your question. Please try rephrasing or contact support.",
                status="error",
                answer_rows=None,
                code=code,
                error=error,
                execution_log=execution_log,
            )

        return ChatResponse(
            answer=str(answer) if answer else "No answer generated",
            status=status,
            answer_rows=answer_rows,
            code=code,
            error=None,
            execution_log=execution_log,
        )

    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/health")
def chat_health() -> dict[str, str]:
    """
    Health check endpoint for the chat service.

    Returns:
        Status message indicating service health
    """
    return {
        "status": "healthy",
        "service": "risk-sme-chat",
        "message": "Chat service is operational",
    }
