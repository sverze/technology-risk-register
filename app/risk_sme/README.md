# Risk SME (Subject Matter Expert) Agent

A chat-based AI agent that generates and executes SQLAlchemy queries against the Technology Risk Register database. Ask natural language questions and get instant answers about your risks.

## 🎯 What It Does

The Risk SME Agent uses Claude (Anthropic) to:
1. **Understand your question** in natural language
2. **Generate SQLAlchemy code** to query the risk database
3. **Execute the code safely** in a read-only sandbox
4. **Return formatted results** with both natural language summaries and structured data

## 🚀 Quick Start

### Run a Single Query

```bash
cd aisuite/risk_sme
uv run python risk_sme_agent.py
```

By default, this runs the example query: "Show me all critical risks in the Infrastructure domain"

### Interactive Mode

```bash
uv run python test_queries.py --interactive
```

Type questions one at a time and get instant answers.

### Run Test Suite

```bash
uv run python test_queries.py
```

Runs a comprehensive test suite covering different query patterns.

## 📝 Example Queries

### Simple Filters
- "Show me all critical risks"
- "What risks are currently active?"
- "Find all risks in the Infrastructure domain"
- "Show me risks owned by the Security team"

### Date Queries
- "Which risks were reviewed in the last 30 days?"
- "Show me risks that haven't been reviewed in over 90 days"
- "What risks are due for review this month?"

### Multi-Condition
- "Show me critical infrastructure risks that are active"
- "Find high or critical risks in the Cloud or Infrastructure domains"

### Text Search
- "Find risks related to databases"
- "Show me risks with 'failure' in the title"
- "Search for risks mentioning 'authentication' or 'access'"

### Aggregations
- "How many risks are in each technology domain?"
- "Count risks by status"
- "What's the distribution of risk exposures?"

### Complex Queries
- "Show me the top 5 risks by exposure that are active and haven't been reviewed in 60 days"
- "Which Infrastructure risks have financial impact greater than $100,000?"

## 🏗️ Architecture

### Components

```
aisuite/risk_sme/
├── risk_utils.py              # Schema introspection & helpers
├── risk_sme_agent.py          # Main agent (generation + execution)
├── test_queries.py            # Test suite & interactive mode
└── README.md                  # This file
```

### How It Works

```
User Question
     ↓
┌────────────────────────────────┐
│  1. Schema Introspection       │  ← risk_utils.build_schema_block()
│     - Table structures          │
│     - Sample data               │
│     - Valid dropdown values     │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│  2. LLM Code Generation        │  ← Claude Sonnet 4
│     - Anthropic API             │
│     - Temperature: 0.2          │
│     - Prompt with examples      │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│  3. Safe Execution             │  ← execute_generated_code()
│     - Controlled namespace      │
│     - Read-only session         │
│     - No dangerous operations   │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│  4. Formatted Results          │
│     - Natural language answer   │
│     - Structured data (JSON)    │
│     - Execution logs            │
└────────────────────────────────┘
```

## 🔒 Safety Features

### Read-Only by Default
- Only `session.query()` is allowed
- No `.add()`, `.delete()`, or `.commit()` operations
- Database mutations are blocked

### Controlled Sandbox
The execution environment only provides:
- SQLAlchemy models: `Risk`, `RiskLogEntry`, `DropdownValue`
- Query helpers: `and_`, `or_`, `func`
- Date utilities: `date`, `datetime`, `timedelta`
- Session object (read-only)

### Code Auditing
- All generated code is visible
- Execution logs show what queries ran
- Use `show_details=True` in test_queries.py to inspect generated code

## 🔧 Customization

### Change the Default Query

Edit `risk_sme_agent.py` main() function:

```python
def main():
    session = SessionLocal()
    try:
        question = "Your custom question here"
        result = risk_sme_agent(question, session=session)
    finally:
        session.close()
```

### Add Your Own Test Queries

Edit `test_queries.py` and add to any category:

```python
CUSTOM_QUERIES = [
    "Your first question",
    "Your second question",
]
```

### Adjust Temperature

Higher temperature (0.5-1.0) = More creative queries
Lower temperature (0.0-0.2) = More deterministic queries

```python
result = risk_sme_agent(
    question,
    session=session,
    temperature=0.5,  # Default is 0.2
)
```

## 📊 Output Formats

The agent returns three types of output:

### 1. Natural Language Answer (`answer_text`)
```
I found 12 active risks in the system. These span multiple technology
domains and risk categories, with exposure levels ranging from low to critical.
```

### 2. Structured Data (`answer_rows`)
```python
[
    {
        'risk_id': 'TR-2025-001',
        'title': 'Enterprise Data Loss Event',
        'category': 'Data Management',
        'exposure': 'Critical (15)',
        ...
    },
    ...
]
```

### 3. Status Codes
- `success` - Query executed and returned results
- `no_results` - Query executed but found no matching records
- `invalid_request` - Unable to parse the question
- `error` - Technical error during execution

## 🐛 Troubleshooting

### "Module not found" errors

Make sure you're running from the `aisuite/risk_sme/` directory:
```bash
cd aisuite/risk_sme
uv run python risk_sme_agent.py
```

### Database connection errors

Verify the risk_register.db exists:
```bash
ls ../../risk_register.db
```

If missing, run the FastAPI backend first to create it:
```bash
cd ../..
uv run uvicorn app.main:app --reload
```

### Empty results

Check if your database has data:
```python
from app.core.database import SessionLocal
from app.models.risk import Risk

session = SessionLocal()
count = session.query(Risk).count()
print(f"Total risks in database: {count}")
session.close()
```

## 🔮 Future Enhancements

### Phase 1 (Current) ✅
- [x] Read-only query generation
- [x] SQLAlchemy ORM support
- [x] Command-line interface
- [x] Test suite with examples

### Phase 2 (Planned)
- [ ] FastAPI endpoint: `POST /api/v1/chat`
- [ ] Frontend chat UI component
- [ ] Query result caching
- [ ] Query history logging

### Phase 3 (Future)
- [ ] Mutation support (with approval workflow)
- [ ] Multi-turn conversations
- [ ] Saved query templates
- [ ] Export results (CSV, PDF)

## 📚 Related Files

- `/app/models/risk.py` - SQLAlchemy model definitions
- `/app/core/database.py` - Database session management
- `/aisuite/customer/` - Original customer service agent (TinyDB version)

## 🤝 Contributing

To add new query patterns or improve the agent:

1. **Add examples to test_queries.py** - Help improve test coverage
2. **Enhance the prompt in risk_sme_agent.py** - Add domain-specific guidance
3. **Extend risk_utils.py** - Add helper functions for common operations

## ⚠️ Important Notes

- This is a **read-only** agent - no data mutations
- Generated code is **executed in a sandbox** - only approved imports available
- **Temperature is low (0.2)** for consistent, deterministic queries
- **Anthropic API key required** - set in .env file

## 📖 Learn More

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Risk Register API Docs](../../docs/api.md)
