from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.app.agents.sql_agent import run_sql_agent
from backend.app.agents.vision_agent import run_vision_agent
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


def supervisor(
    state: OmniBrainState,
) -> OmniBrainState:

    query = state.get("query", "").strip()

    if not query:
        return {
            "route": "search",
            "agent_trace": [
                "supervisor",
                "invalid_query",
            ],
            "error": "Query cannot be empty.",
        }

    route = _classify_query(query)

    return {
        "route": route,
        "agent_trace": [
            "supervisor",
            f"route:{route}",
        ],
    }


def search_agent(
    state: OmniBrainState,
) -> OmniBrainState:

    query = state["query"]
    top_k = state.get("top_k", 5)

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
    top_k = state.get("top_k", 3)

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

    graph.add_node(
        "supervisor",
        supervisor,
    )

    graph.add_node(
        "search_agent",
        search_agent,
    )

    graph.add_node(
        "sql_agent",
        sql_agent,
    )

    graph.add_node(
        "vision_agent",
        vision_agent,
    )

    graph.add_edge(
        START,
        "supervisor",
    )

    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "search_agent": "search_agent",
            "sql_agent": "sql_agent",
            "vision_agent": "vision_agent",
        },
    )

    graph.add_edge(
        "search_agent",
        END,
    )

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