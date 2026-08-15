from pathlib import Path
import sqlite3
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "omnibrain.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)


def execute_query(
    query: str,
    parameters: tuple = (),
) -> List[Dict[str, Any]]:
    normalized = query.strip().lower()

    if not normalized:
        raise ValueError("SQL query cannot be empty.")

    if not normalized.startswith("select"):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    blocked_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "replace",
        "attach",
        "detach",
        "pragma",
    ]

    for keyword in blocked_keywords:
        if f"{keyword} " in f"{normalized} ":
            raise ValueError(
                f"SQL operation '{keyword.upper()}' is not allowed."
            )

    with get_connection() as connection:
        cursor = connection.execute(
            query,
            parameters,
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


def seed_demo_transaction() -> None:
    initialize_database()

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM transactions
            """
        ).fetchone()["count"]

        if existing > 0:
            return

        connection.execute(
            """
            INSERT INTO transactions (
                payment_date,
                transaction_date,
                transaction_amount,
                surcharge_amount,
                bank_transaction_id,
                transaction_status,
                bank_name,
                payment_method,
                card_holder_name,
                email,
                mobile,
                address,
                transaction_description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "14/12/2023",
                "2023-12-14 17:48:33",
                1800.00,
                None,
                "371420584249",
                None,
                None,
                "Card",
                None,
                None,
                None,
                None,
                None,
            ),
        )

        connection.commit()
