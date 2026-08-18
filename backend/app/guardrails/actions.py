from typing import Optional

from nemoguardrails.actions import action


ALLOWED_TERMS = {
    "document",
    "pdf",
    "file",
    "uploaded",
    "transaction",
    "payment",
    "amount",
    "bank",
    "account",
    "record",
    "records",
    "table",
    "database",
    "sql",
    "row",
    "rows",
    "chart",
    "graph",
    "image",
    "picture",
    "photo",
    "figure",
    "diagram",
    "visual",
    "bar",
    "pie",
    "line",
    "data",
    "value",
    "total",
    "sum",
    "average",
    "maximum",
    "minimum",
    "company",
    "financial",
    "report",
    "belong",
}


def is_document_scope_query(
    query: str,
) -> bool:
    """Deterministic document/data scope check."""

    if not query:
        return False

    words = set(
        query.lower()
        .strip()
        .replace("?", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace(";", " ")
        .replace(":", " ")
        .replace("!", " ")
        .split()
    )

    return bool(
        words.intersection(ALLOWED_TERMS)
    )


@action(is_system_action=True)
async def check_document_scope(
    context: Optional[dict] = None,
):
    """NeMo Guardrails action for document scope."""

    context = context or {}

    user_message = context.get(
        "user_message"
    )

    if not user_message:
        user_message = context.get(
            "last_user_message",
            "",
        )

    return is_document_scope_query(
        user_message
    )
