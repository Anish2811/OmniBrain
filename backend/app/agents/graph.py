from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.app.agents.sql_agent import run_sql_agent
from backend.app.agents.vision_agent import run_vision_agent
from backend.app.guardrails.actions import is_document_scope_query
from ingestion.retrieval import DocumentRetriever


class OmniBrainState(TypedDict, total=False):
    query: str
    top_k: int
    route: str
    results: list
    context: str
    answer: str
    citations: list
    agent_trace: list
    error: str

    # Self-RAG state
    retrieval_relevant: bool
    retry_count: int
    max_retries: int
    rewritten_query: str


def _classify_query(
    query: str,
) -> Literal["search", "sql", "vision"]:

    query_lower = query.lower()

    sql_keywords = [
        "sql",
        "database",
        "table",
        "rows",
        "records",
        "count",
        "sum",
        "average",
        "total",
        "maximum",
        "minimum",
        "group by",
        "how many",
    ]

    vision_keywords = [
        "image",
        "picture",
        "photo",
        "chart",
        "graph",
        "diagram",
        "figure",
        "visual",
        "bar chart",
        "pie chart",
        "line chart",
    ]

    if any(
        keyword in query_lower
        for keyword in vision_keywords
    ):
        return "vision"

    if any(
        keyword in query_lower
        for keyword in sql_keywords
    ):
        return "sql"

    return "search"


def guardrail(
    state: OmniBrainState,
) -> OmniBrainState:

    query = state.get(
        "query",
        "",
    ).strip()

    trace = list(
        state.get(
            "agent_trace",
            [],
        )
    )

    allowed = is_document_scope_query(
        query
    )

    if allowed:
        trace.append(
            "guardrail:allowed"
        )

        return {
            "agent_trace": trace,
        }

    trace.append(
        "guardrail:blocked"
    )

    return {
        "answer": (
            "I can only answer questions "
            "based on the uploaded documents."
        ),
        "results": [],
        "context": "",
        "citations": [],
        "error": "Query is outside document scope.",
        "agent_trace": trace,
        "route": "blocked",
    }


def supervisor(
    state: OmniBrainState,
) -> OmniBrainState:

    query = state.get(
        "query",
        "",
    ).strip()

    if not query:
        return {
            "route": "search",
            "agent_trace": [
                "supervisor",
                "invalid_query",
            ],
            "error": "Query cannot be empty.",
        }

    route = _classify_query(
        query
    )

    return {
        "route": route,
        "agent_trace": [
            "supervisor",
            f"route:{route}",
        ],
        "retry_count": 0,
        "max_retries": 1,
    }


def search_agent(
    state: OmniBrainState,
) -> OmniBrainState:

    query = state["query"]

    top_k = state.get(
        "top_k",
        5,
    )

    retriever = DocumentRetriever()

    results = retriever.retrieve(
        query,
        top_k=top_k,
    )

    context_parts = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        metadata = result.get(
            "metadata",
            {},
        )

        text = metadata.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        document = metadata.get(
            "document",
            "unknown",
        )

        page_number = metadata.get(
            "page_number",
        )

        source_label = (
            f"Source {index} ({document}"
        )

        if page_number is not None:
            source_label += (
                f", page {page_number}"
            )

        source_label += ")"

        context_parts.append(
            f"{source_label}:\n{text}"
        )

    context = "\n\n".join(
        context_parts
    )

    trace = list(
        state.get(
            "agent_trace",
            [],
        )
    )

    trace.extend(
        [
            "search_agent",
            "qdrant",
        ]
    )

    return {
        "results": results,
        "context": context,
        "agent_trace": trace,
    }


def evaluate_retrieval(
    state: OmniBrainState,
) -> OmniBrainState:

    results = state.get(
        "results",
        [],
    )

    retry_count = state.get(
        "retry_count",
        0,
    )

    max_retries = state.get(
        "max_retries",
        1,
    )

    trace = list(
        state.get(
            "agent_trace",
            [],
        )
    )

    if not results:
        relevant = False

    else:
        scores = []

        for result in results:
            score = result.get(
                "score"
            )

            if score is not None:
                try:
                    scores.append(
                        float(score)
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

        if not scores:
            relevant = False
        else:
            best_score = max(scores)

            # Qdrant cosine similarity threshold.
            relevant = best_score >= 0.20

    if relevant:
        trace.append(
            "retrieval_evaluator:relevant"
        )

    else:
        trace.append(
            "retrieval_evaluator:irrelevant"
        )

    if retry_count >= max_retries:
        trace.append(
            "self_rag:max_retries_reached"
        )

        if not relevant:
            return {
                "retrieval_relevant": False,
                "results": [],
                "context": "",
                "answer": (
                    "I could not find relevant information "
                    "in the uploaded documents."
                ),
                "citations": [],
                "agent_trace": trace,
            }

    return {
        "retrieval_relevant": relevant,
        "agent_trace": trace,
    }


def rewrite_query(
    state: OmniBrainState,
) -> OmniBrainState:

    original_query = state.get(
        "query",
        "",
    ).strip()

    retry_count = state.get(
        "retry_count",
        0,
    )

    trace = list(
        state.get(
            "agent_trace",
            [],
        )
    )

    # Lightweight deterministic query rewriting.
    # Keeps Self-RAG testable without an external LLM.
    stop_words = {
        "what",
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "does",
        "do",
        "did",
        "show",
        "tell",
        "me",
        "about",
        "please",
        "can",
        "you",
        "of",
        "for",
        "in",
        "on",
        "to",
    }

    words = (
        original_query
        .replace("?", "")
        .split()
    )

    meaningful_words = [
        word
        for word in words
        if word.lower() not in stop_words
    ]

    if meaningful_words:
        rewritten_query = " ".join(
            meaningful_words
        )
    else:
        rewritten_query = original_query

    trace.extend(
        [
            "self_rag",
            "query_rewriter",
        ]
    )

    return {
        "query": rewritten_query,
        "rewritten_query": rewritten_query,
        "retry_count": retry_count + 1,
        "agent_trace": trace,
    }


def route_after_retrieval(
    state: OmniBrainState,
) -> str:

    relevant = state.get(
        "retrieval_relevant",
        False,
    )

    retry_count = state.get(
        "retry_count",
        0,
    )

    max_retries = state.get(
        "max_retries",
        1,
    )

    if relevant:
        return "finish_search"

    if retry_count < max_retries:
        return "rewrite_query"

    return "finish_search"


def sql_agent(
    state: OmniBrainState,
) -> OmniBrainState:

    query = state["query"]

    result = run_sql_agent(
        query,
    )

    trace = list(
        state.get(
            "agent_trace",
            [],
        )
    )

    trace.extend(
        [
            "sql_agent",
            "sqlite",
        ]
    )

    return {
        "results": result["rows"],
        "context": str(
            result["rows"]
        ),
        "answer": str(
            result["rows"]
        ),
        "agent_trace": trace,
    }


def vision_agent(
    state: OmniBrainState,
) -> OmniBrainState:

    query = state["query"]

    top_k = state.get(
        "top_k",
        3,
    )

    result = run_vision_agent(
        query=query,
        top_k=top_k,
    )

    trace = list(
        state.get(
            "agent_trace",
            [],
        )
    )

    trace.extend(
        result.get(
            "agent_trace",
            ["vision_agent"],
        )
    )

    return {
        "results": result.get(
            "results",
            [],
        ),
        "context": str(
            result.get(
                "results",
                [],
            )
        ),
        "answer": result.get(
            "answer",
            "",
        ),
        "citations": result.get(
            "citations",
            [],
        ),
        "agent_trace": trace,
    }


def route_after_guardrail(
    state: OmniBrainState,
) -> str:

    if state.get("error"):
        return "blocked"

    return "supervisor"


def route_after_supervisor(
    state: OmniBrainState,
) -> str:

    route = state.get(
        "route",
        "search",
    )

    if route == "sql":
        return "sql_agent"

    if route == "vision":
        return "vision_agent"

    return "search_agent"


def build_omnibrain_graph():

    graph = StateGraph(
        OmniBrainState
    )

    # Guardrail
    graph.add_node(
        "guardrail",
        guardrail,
    )

    # Supervisor
    graph.add_node(
        "supervisor",
        supervisor,
    )

    # Agents
    graph.add_node(
        "search_agent",
        search_agent,
    )

    graph.add_node(
        "evaluate_retrieval",
        evaluate_retrieval,
    )

    graph.add_node(
        "rewrite_query",
        rewrite_query,
    )

    graph.add_node(
        "sql_agent",
        sql_agent,
    )

    graph.add_node(
        "vision_agent",
        vision_agent,
    )

    # START → Guardrail
    graph.add_edge(
        START,
        "guardrail",
    )

    # Guardrail → Supervisor / Block
    graph.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "supervisor": "supervisor",
            "blocked": END,
        },
    )

    # Supervisor → Agent
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "search_agent": "search_agent",
            "sql_agent": "sql_agent",
            "vision_agent": "vision_agent",
        },
    )

    # Search → Retrieval Evaluation
    graph.add_edge(
        "search_agent",
        "evaluate_retrieval",
    )

    # Self-RAG Decision
    graph.add_conditional_edges(
        "evaluate_retrieval",
        route_after_retrieval,
        {
            "finish_search": END,
            "rewrite_query": "rewrite_query",
        },
    )

    # Rewritten query → Search again
    graph.add_edge(
        "rewrite_query",
        "search_agent",
    )

    # SQL / Vision → END
    graph.add_edge(
        "sql_agent",
        END,
    )

    graph.add_edge(
        "vision_agent",
        END,
    )

    return graph.compile()


omnibrain_graph = build_omnibrain_graph()