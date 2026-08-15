from typing import Any, Dict, List

from database.sql_queries import (
    execute_query,
    initialize_database,
    seed_demo_transaction,
)


class SQLAgent:

    def __init__(self) -> None:
        initialize_database()
        seed_demo_transaction()

    def run(
        self,
        query: str,
    ) -> Dict[str, Any]:

        if not query or not query.strip():
            raise ValueError(
                "SQL agent query cannot be empty."
            )

        sql = self._build_sql(query)

        rows = execute_query(sql)

        return {
            "sql": sql,
            "rows": rows,
        }

    @staticmethod
    def _build_sql(
        query: str,
    ) -> str:

        query_lower = query.lower()

        if (
            "total transaction amount" in query_lower
            or "sum transaction amount" in query_lower
        ):
            return """
                SELECT
                    SUM(transaction_amount)
                    AS total_transaction_amount
                FROM transactions
            """

        if (
            "average transaction amount" in query_lower
            or "average transaction" in query_lower
        ):
            return """
                SELECT
                    AVG(transaction_amount)
                    AS average_transaction_amount
                FROM transactions
            """

        if (
            "transaction amount" in query_lower
            or "transaction" in query_lower
        ):
            return """
                SELECT
                    id,
                    payment_date,
                    transaction_date,
                    transaction_amount,
                    bank_transaction_id,
                    transaction_status
                FROM transactions
                ORDER BY transaction_date DESC
                LIMIT 10
            """

        if "count" in query_lower:
            return """
                SELECT
                    COUNT(*) AS transaction_count
                FROM transactions
            """

        raise ValueError(
            "The SQL agent could not determine a supported "
            "structured-data operation."
        )


def run_sql_agent(
    query: str,
) -> Dict[str, Any]:

    agent = SQLAgent()

    result = agent.run(query)

    return {
        "sql": result["sql"],
        "rows": result["rows"],
        "agent_trace": ["sql_agent"],
    }
