from fastapi import APIRouter, HTTPException

from backend.app.agents.sql_agent import run_sql_agent


router = APIRouter(tags=["SQL"])


@router.post("/sql")
async def sql(query: str):

    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail="SQL query cannot be empty.",
        )

    try:
        result = run_sql_agent(
            query.strip()
        )

        return {
            "query": query.strip(),
            "sql": result["sql"],
            "rows": result["rows"],
            "agent_trace": [
                "sql_agent",
                "sqlite",
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="SQL agent failed to process the request.",
        )