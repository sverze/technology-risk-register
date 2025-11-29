"""
Risk SME (Subject Matter Expert) Agent

A chat-based agent that generates and executes SQLAlchemy queries against
the Technology Risk Register database. Based on the customer service agent pattern.
"""

import io
import json
import math
import re
import statistics
import sys
import traceback
from datetime import date, datetime, timedelta
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.risk import DropdownValue, Risk, RiskLogEntry
from app.risk_sme import risk_utils

load_dotenv()
client = Anthropic()


# ==========================
# PROMPT TEMPLATE
# ==========================

PROMPT = """You are a Risk Management Subject Matter Expert assistant. ANSWER USER QUESTIONS BY WRITING PYTHON CODE USING SQLALCHEMY.

Database Schema & Samples (read-only):
{schema_block}

Execution Environment (already imported/provided):
- Variables:
  * session: Session  # SQLAlchemy Session object for database queries
  * Risk, RiskLogEntry, DropdownValue  # SQLAlchemy model classes
  * and_, or_, func  # SQLAlchemy query helpers
  * date, datetime, timedelta  # datetime utilities
  * user_request: str  # the original user question

- Modules available (no import needed):
  * re - Regular expressions for string parsing/matching
  * json - JSON encoding/decoding
  * math - Mathematical functions (sqrt, floor, ceil, etc.)
  * statistics - Statistical calculations (mean, median, stdev, etc.)
  * All Python built-ins: len, str, int, float, min, max, sum, sorted, any, all, enumerate, zip, range

- Query Examples:
  ```python
  # Simple filter
  risks = session.query(Risk).filter(Risk.risk_status == "Active").all()

  # Multiple conditions
  from sqlalchemy import and_
  risks = session.query(Risk).filter(and_(
      Risk.technology_domain == "Infrastructure",
      Risk.business_disruption_net_exposure.like("Critical%")
  )).all()

  # Date range query
  from datetime import date, timedelta
  thirty_days_ago = date.today() - timedelta(days=30)
  risks = session.query(Risk).filter(Risk.last_reviewed >= thirty_days_ago).all()

  # Access relationships
  risk = session.query(Risk).first()
  log_entries = risk.log_entries  # List of RiskLogEntry objects
  log_count = len(risk.log_entries)

  # Aggregation
  from sqlalchemy import func
  count_by_domain = session.query(
      Risk.technology_domain,
      func.count(Risk.risk_id)
  ).group_by(Risk.technology_domain).all()
  ```

QUERY RULES (critical):
- Derive ALL filters/parameters from user_request (keywords, domains, owners, statuses, date ranges)
- Do NOT hard-code values unless explicitly stated in user_request
- Build SQLAlchemy queries dynamically using .filter()
- If a constraint isn't in user_request, don't apply it
- This is READ-ONLY: Do NOT use session.add(), session.delete(), or session.commit()
- Only use session.query() for retrieving data

HUMAN RESPONSE REQUIREMENT (hard):
- You MUST set a variable named `answer_text` (type str) with a clear, helpful answer (1-3 sentences)
- This is the primary user-facing message
- If data is found, summarize key findings
- If no data matches, explain why and suggest alternatives
- Use natural language, not technical jargon

DATA PRESENTATION:
- Also set `answer_rows` (list[dict]) with structured results when appropriate
- Each dict should contain key fields: id, title, category, status, owner, exposure, etc.
- Keep answer_rows to reasonable size (max 20 items, use .limit() if needed)
- For large result sets, provide summary stats in answer_text and top N in answer_rows

STATUS VARIABLE (required):
- Always set a string `STATUS` to one of:
  * "success" - Query executed and returned results
  * "no_results" - Query executed but found no matching records
  * "invalid_request" - Unable to parse the question or missing information
  * "error" - Query failed due to technical issue

FAILURE & EDGE-CASE HANDLING:
- no_results: No records match the filters → suggest broadening criteria or nearby alternatives
- invalid_request: Can't understand the question → ask for clarification politely
- error: Technical error → explain what went wrong in simple terms

OUTPUT CONTRACT:
- Return ONLY executable Python between these tags (no extra text):
  <execute_python>
  # your python code here
  </execute_python>

CODE CHECKLIST (follow in code):
1) Parse intent & constraints from user_request (use regex if helpful)
2) Build SQLAlchemy query using session.query(Risk).filter(...)
3) Execute query and collect results
4) ALWAYS set:
   - `answer_text` (human-readable summary, required)
   - `STATUS` (see list above, required)
   - `answer_rows` (structured data, optional but recommended)
5) Add a brief log to stdout, e.g., "LOG: Found 5 risks matching criteria. STATUS=success"

TONE EXAMPLES (for `answer_text`):
- success: "I found 7 critical infrastructure risks. The most recent is 'Database Failure' owned by John Smith."
- no_results: "I couldn't find any risks in the Cloud domain with high exposure. There are 3 medium-exposure cloud risks available."
- invalid_request: "I'd be happy to help! Which technology domain are you interested in?"
- error: "I encountered an issue with the date format. Could you specify the date as YYYY-MM-DD?"

Constraints:
- Use SQLAlchemy ORM for all queries (never raw SQL)
- Keep code clear and commented with numbered steps
- Standard library imports only if needed (already have datetime, etc.)

User request:
{question}
"""


# ==========================
# CODE GENERATION
# ==========================


def generate_llm_code(
    prompt: str,
    *,
    session: Session,
    model: str = "claude-sonnet-4-20250514",
    temperature: float = 0.2,
) -> str:
    """
    Ask the LLM to produce a plan-with-code response for the user's question.
    Returns the FULL assistant content (including <execute_python> tags).
    """
    schema_block = risk_utils.build_schema_block(session)
    full_prompt = PROMPT.format(schema_block=schema_block, question=prompt)

    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=temperature,
        system="You are a risk management expert who writes safe, well-commented SQLAlchemy code to answer questions about technology risks.",
        messages=[
            {"role": "user", "content": full_prompt},
        ],
    )
    content = resp.content[0].text or ""  # type: ignore[union-attr]

    return content


# ==========================
# CODE EXTRACTION
# ==========================


def _extract_execute_block(text: str) -> str:
    """
    Returns the Python code inside <execute_python>...</execute_python>.
    If no tags are found, assumes 'text' is already raw Python code.
    """
    if not text:
        raise RuntimeError("Empty content passed to code executor.")
    m = re.search(r"<execute_python>(.*?)</execute_python>", text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else text.strip()


# ==========================
# SAFE CODE EXECUTION
# ==========================


def execute_generated_code(
    code_or_content: str,
    *,
    session: Session,
    user_request: str | None = None,
) -> dict[str, Any]:
    """
    Execute generated code in a controlled namespace.
    Accepts either raw Python code OR full content with <execute_python> tags.
    Returns artifacts: stdout, error, and extracted answer.
    """
    # Extract code from tags
    code = _extract_execute_block(code_or_content)

    # Define safe execution environment (READ-ONLY)
    SAFE_GLOBALS = {
        # SQLAlchemy
        "session": session,
        "Risk": Risk,
        "RiskLogEntry": RiskLogEntry,
        "DropdownValue": DropdownValue,
        "and_": and_,
        "or_": or_,
        "func": func,
        # Date/time utilities
        "date": date,
        "datetime": datetime,
        "timedelta": timedelta,
        # Standard library utilities (safe - no I/O)
        "re": re,
        "json": json,
        "math": math,
        "statistics": statistics,
        # Built-in functions for data manipulation
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "min": min,
        "max": max,
        "sum": sum,
        "sorted": sorted,
        "any": any,
        "all": all,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
        "print": print,
        # User context
        "user_request": user_request or "",
    }
    SAFE_LOCALS: dict[str, object] = {}

    # Capture stdout from the executed code
    _stdout_buf, _old_stdout = io.StringIO(), sys.stdout
    sys.stdout = _stdout_buf
    err_text = None

    try:
        exec(code, SAFE_GLOBALS, SAFE_LOCALS)
    except Exception:
        err_text = traceback.format_exc()
    finally:
        sys.stdout = _old_stdout

    printed = _stdout_buf.getvalue().strip()

    # Extract possible answers set by the generated code
    answer = SAFE_LOCALS.get("answer_text") or SAFE_LOCALS.get("answer_rows") or SAFE_LOCALS.get("answer_json")
    status = SAFE_LOCALS.get("STATUS", "unknown")

    return {
        "code": code,
        "stdout": printed,
        "error": err_text,
        "answer": answer,
        "status": status,
        "answer_rows": SAFE_LOCALS.get("answer_rows"),
    }


# ==========================
# MAIN AGENT FUNCTION
# ==========================


def risk_sme_agent(
    question: str,
    *,
    session: Session,
    model: str = "claude-sonnet-4-5-20250929",
    temperature: float = 0.2,
) -> dict[str, Any]:
    """
    End-to-end risk SME agent:
      1) Generate SQLAlchemy code from question
      2) Execute in a controlled namespace
      3) Return results

    Returns:
      {
        "full_content": <raw LLM response>,
        "exec": {
            "code": <extracted python>,
            "stdout": <execution logs>,
            "error": <traceback or None>,
            "answer": <answer_text/rows/json>,
            "status": <success/no_results/invalid_request/error>,
            "answer_rows": <structured data if available>
        }
      }
    """
    # 1) Show the question
    print(f"\n{'━' * 80}")
    print("💬 USER QUESTION")
    print(f"{'━' * 80}")
    print(question)
    print()

    # 2) Generate code
    print(f"{'━' * 80}")
    print("🤖 GENERATING QUERY CODE...")
    print(f"{'━' * 80}\n")

    full_content = generate_llm_code(
        question,
        session=session,
        model=model,
        temperature=temperature,
    )

    # 3) Execute
    exec_res = execute_generated_code(
        full_content,
        session=session,
        user_request=question,
    )

    # 3.5) Retry with feedback if first attempt failed
    if exec_res["error"]:
        print(f"\n{'⚠' * 80}")
        print("⚠️  RETRY: First attempt failed, asking LLM to fix the error...")
        print(f"{'⚠' * 80}\n")

        # Create feedback prompt with error details
        retry_prompt = f"""Your previous code failed with this error:

```
{exec_res["error"]}
```

Original question: {question}

Your failed code:
```python
{exec_res["code"]}
```

Please fix the error and provide corrected code. Common issues:
- NameError: Module not imported (available modules: re, json, math, statistics)
- AttributeError: Check field names match the Risk model schema
- TypeError: Ensure proper type conversions (str to int, date parsing, etc.)
- Missing null checks: Use `.filter(Risk.field != None)` for null safety

Important reminders:
- All modules (re, json, math, statistics) are already available - do NOT import them
- SQLAlchemy queries must use .filter() not raw SQL
- Always set answer_text, STATUS, and answer_rows variables
- Use .like() for string matching, .filter() for exact matches

Return ONLY the corrected code in <execute_python> tags."""

        # Generate fixed code
        print(f"{'━' * 80}")
        print("🔧 GENERATING FIXED CODE...")
        print(f"{'━' * 80}\n")

        retry_content = generate_llm_code(
            retry_prompt,
            session=session,
            model=model,
            temperature=temperature,
        )

        # Execute fixed code
        exec_res = execute_generated_code(
            retry_content,
            session=session,
            user_request=question,
        )

        # Update full_content to include retry attempt
        full_content = f"{full_content}\n\n---RETRY ATTEMPT---\n\n{retry_content}"

        if exec_res["error"]:
            print(f"\n{'❌' * 80}")
            print("❌ RETRY FAILED: Code still has errors after fix attempt")
            print(f"{'❌' * 80}\n")
        else:
            print(f"\n{'✅' * 80}")
            print("✅ RETRY SUCCEEDED: Fixed code executed successfully!")
            print(f"{'✅' * 80}\n")

    # 4) Show results
    if exec_res["error"]:
        print(f"\n{'=' * 80}")
        print("❌ EXECUTION ERROR")
        print(f"{'=' * 80}")
        print(exec_res["error"])
        print(f"{'=' * 80}\n")
    else:
        print(f"\n{'=' * 80}")
        print("✅ ANSWER")
        print(f"{'=' * 80}")
        print(exec_res["answer"] or "No answer generated")
        print(f"{'=' * 80}\n")

        if exec_res["answer_rows"]:
            print(f"{'─' * 80}")
            print(f"📊 STRUCTURED RESULTS ({len(exec_res['answer_rows'])} records)")
            print(f"{'─' * 80}")
            for i, row in enumerate(exec_res["answer_rows"][:10], 1):  # Show first 10
                print(f"{i}. {row}")
            if len(exec_res["answer_rows"]) > 10:
                print(f"... and {len(exec_res['answer_rows']) - 10} more")
            print()

    if exec_res["stdout"]:
        print(f"{'─' * 80}")
        print("📝 EXECUTION LOG")
        print(f"{'─' * 80}")
        print(exec_res["stdout"])
        print()

    # 5) Return artifacts
    return {
        "full_content": full_content,
        "exec": exec_res,
    }


# ==========================
# CLI INTERFACE
# ==========================


def main():
    """
    Command-line interface for the Risk SME Agent.
    """
    # Create database session
    session = SessionLocal()

    try:
        # Example query - replace with user input
        question = "Show me all risks  that have a Financial Impact > $250000"

        result = risk_sme_agent(
            question,
            session=session,
            model="claude-sonnet-4-5-20250929",
            temperature=0.8,
        )

        print(f"\n{'=' * 80}")
        print("✨ SESSION COMPLETE")
        print(f"{'=' * 80}")
        print(f"Status: {result['exec']['status']}")
        print(f"{'=' * 80}\n")

    finally:
        session.close()


if __name__ == "__main__":
    main()
