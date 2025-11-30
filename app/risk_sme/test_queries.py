"""
Test Queries for Risk SME Agent

A collection of example questions covering different query patterns and complexity levels.
Use these to test and demonstrate the agent's capabilities.
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from risk_sme_agent import risk_sme_agent

from app.core.database import SessionLocal

# ==========================
# TEST QUERY CATEGORIES
# ==========================

SIMPLE_FILTERS = [
    "Show me all critical risks",
    "What risks are currently active?",
    "Find all risks in the Infrastructure domain",
    "Show me risks owned by the Security team",
    "List all risks with high exposure",
]

DATE_QUERIES = [
    "Which risks were reviewed in the last 30 days?",
    "Show me risks that haven't been reviewed in over 90 days",
    "What risks are due for review this month?",
    "Find risks identified in the last quarter",
]

MULTI_CONDITION = [
    "Show me critical infrastructure risks that are active",
    "Find high or critical risks in the Cloud or Infrastructure domains",
    "What active risks are owned by John Smith in the Security domain?",
]

TEXT_SEARCH = [
    "Find risks related to databases",
    "Show me risks with 'failure' in the title",
    "Search for risks mentioning 'authentication' or 'access'",
]

RELATIONSHIPS = [
    "Show me risks that have log entries",
    "Which risks have more than 5 log entries?",
    "Find risks with recent log updates (last 30 days)",
]

AGGREGATIONS = [
    "How many risks are in each technology domain?",
    "Count risks by status",
    "What's the distribution of risk exposures?",
    "How many risks does each owner have?",
]

COMPLEX_QUERIES = [
    "Show me the top 5 risks by exposure that are active and haven't been reviewed in 60 days",
    "Find critical risks with corrective controls rated as 'Not Implemented'",
    "Which Infrastructure risks have financial impact greater than $100,000?",
]

# ==========================
# TEST RUNNER
# ==========================


def run_test_query(session, question: str, show_details: bool = False):
    """
    Run a single test query and display results.
    """
    print(f"\n{'#' * 80}")
    print("# TEST QUERY")
    print(f"{'#' * 80}")

    result = risk_sme_agent(
        question,
        session=session,
        model="claude-sonnet-4-20250514",
        temperature=0.2,
    )

    if show_details:
        print(f"\n{'─' * 80}")
        print("🔍 GENERATED CODE")
        print(f"{'─' * 80}")
        print(result["exec"]["code"])
        print()

    return result


def run_category(session, category_name: str, queries: list[str], max_queries: int = None):
    """
    Run all queries in a category.
    """
    print(f"\n{'=' * 80}")
    print(f"📁 CATEGORY: {category_name}")
    print(f"{'=' * 80}\n")

    queries_to_run = queries[:max_queries] if max_queries else queries

    for i, query in enumerate(queries_to_run, 1):
        print(f"\n[{i}/{len(queries_to_run)}] Testing: {query}")
        result = run_test_query(session, query, show_details=False)

        # Brief summary
        status = result["exec"]["status"]
        error = result["exec"]["error"]

        if error:
            print(f"❌ FAILED: {error[:100]}...")
        elif status == "success":
            print(f"✅ SUCCESS: {status}")
        else:
            print(f"⚠️  {status.upper()}")

        print(f"{'─' * 80}")


def main():
    """
    Run all test queries or specific categories.
    """
    session = SessionLocal()

    try:
        print(f"\n{'=' * 80}")
        print("🧪 RISK SME AGENT - TEST SUITE")
        print(f"{'=' * 80}\n")

        # Run one query from each category as a smoke test
        print("Running smoke test (1 query per category)...\n")

        categories = [
            ("Simple Filters", SIMPLE_FILTERS),
            ("Date Queries", DATE_QUERIES),
            ("Multi-Condition", MULTI_CONDITION),
            ("Text Search", TEXT_SEARCH),
            ("Relationships", RELATIONSHIPS),
            ("Aggregations", AGGREGATIONS),
            ("Complex Queries", COMPLEX_QUERIES),
        ]

        for cat_name, queries in categories:
            run_category(session, cat_name, queries, max_queries=1)

        print(f"\n{'=' * 80}")
        print("✨ TEST SUITE COMPLETE")
        print(f"{'=' * 80}\n")

        print("To run full category tests, modify main() to remove max_queries limit")
        print("To run a single query with full details, use run_test_query(session, question, show_details=True)")

    finally:
        session.close()


def interactive_mode():
    """
    Interactive mode - ask questions one at a time.
    """
    session = SessionLocal()

    try:
        print(f"\n{'=' * 80}")
        print("💬 RISK SME AGENT - INTERACTIVE MODE")
        print(f"{'=' * 80}\n")
        print("Type your questions about risks, or 'quit' to exit.\n")

        while True:
            question = input("\n❓ Your question: ").strip()

            if question.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!\n")
                break

            if not question:
                continue

            result = risk_sme_agent(
                question,
                session=session,
                model="claude-sonnet-4-20250514",
                temperature=0.2,
            )

            # Optionally show generated code
            show_code = input("\n📝 Show generated code? (y/n): ").strip().lower()
            if show_code == "y":
                print(f"\n{'─' * 80}")
                print("GENERATED CODE:")
                print(f"{'─' * 80}")
                print(result["exec"]["code"])
                print()

    finally:
        session.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
