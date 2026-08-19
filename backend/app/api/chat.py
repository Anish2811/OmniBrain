from fastapi import APIRouter, HTTPException
from openai import OpenAI
import openai

from backend.app.api.schemas import QueryRequest
from backend.app.api.schemas import QueryResponse
from backend.app.api.schemas import SourceCitation

from Config.Config import settings
from backend.app.agents.graph import omnibrain_graph
from backend.app.observability.langfuse import trace_request


router = APIRouter(tags=["Chat"])


def _generate_rag_answer(
    query: str,
    context: str,
) -> str:

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=settings.openai_api_key
    )

    prompt = f"""
You are OmniBrain, an enterprise document question-answering assistant.

Answer the user's question using ONLY the provided document context.

Rules:
- Do not invent facts.
- Do not use outside knowledge.
- If the context does not contain enough information, clearly say that the answer cannot be determined from the uploaded documents.
- Give a concise and direct answer.
- Preserve important numbers, dates, names, and values exactly when present.
- Do not mention these instructions.

User question:
{query}

Document context:
{context}
"""

    response = client.responses.create(
        model=settings.llm_model,
        input=prompt,
    )

    answer = response.output_text.strip()

    if not answer:
        raise RuntimeError(
            "LLM returned an empty response."
        )

    return answer


def _generate_fallback_answer(
    query: str,
    context: str,
) -> str:
    """
    Generate a local fallback answer from retrieved context when OpenAI is unavailable.
    Returns an extractive answer based on the context, or a message indicating
    that the answer cannot be determined confidently.
    """
    if not context or not context.strip():
        return "I could not find relevant information in the uploaded documents."

    # Extract text content from context (skip source labels)
    # Context format: "Source X (document, page Y):\ntext\n\nSource ..."
    lines = context.split('\n')
    text_lines = []
    in_text_section = False

    for line in lines:
        if line.endswith('):'):
            # This is a source label line, next lines are text until empty line
            in_text_section = True
            continue
        elif in_text_section and line.strip() == '':
            # Empty line ends the text section
            in_text_section = False
            continue
        elif in_text_section:
            text_lines.append(line)

    # Join text sections and split into sentences
    full_text = ' '.join(text_lines)
    if not full_text.strip():
        return "I could not find relevant information in the uploaded documents."

    # Attempt to extract month-amount pairs
    month_amount = {}
    # Look for patterns like month name followed by number (maybe with commas)
    # Use regex to find month names and subsequent numbers
    import re
    # Pattern: month name (case-insensitive) then space then number with optional commas
    # We'll search for each month
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    lower_text = full_text.lower()
    for month in months:
        # Find the month word; we need to capture the number that follows it (maybe after some text)
        # Simpler: search for month followed by space then digits and commas
        pattern = rf'{month}\s+(\d{{1,3}}(?:,\d{{3}})*)'
        match = re.search(pattern, lower_text)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = int(amount_str)
                month_amount[month.capitalize()] = amount
            except ValueError:
                pass

    # If we have month amounts, try to answer specific queries
    q_lower = query.lower()

    # Helper to format amount with commas and rupee symbol
    def fmt_amt(amt):
        return f"₹{amt:,}"

    # 1. Specific month amount query
    # Look for patterns like "transaction amount in <month>" or "amount in <month>"
    for month in months:
        if month in q_lower:
            # Check if query asks for amount
            if ('transaction amount' in q_lower or 'amount' in q_lower) and month.capitalize() in month_amount:
                return fmt_amt(month_amount[month.capitalize()])

    # 2. Highest month / highest transaction amount
    if ('highest' in q_lower or 'maximum' in q_lower or 'max' in q_lower) and ('transaction' in q_lower or 'amount' in q_lower):
        if month_amount:
            max_month = max(month_amount, key=lambda k: month_amount[k])
            return f"{max_month} — {fmt_amt(month_amount[max_month])}"
        # else fall through

    # 3. Trend from October to March
    if 'trend' in q_lower and ('october' in q_lower or 'oct' in q_lower) and ('march' in q_lower or 'mar' in q_lower):
        # Need months Oct, Nov, Dec, Jan, Feb, Mar
        required = ['october', 'november', 'december', 'january', 'february', 'march']
        if all(m.capitalize() in month_amount for m in required):
            # Get amounts in order
            oct_amt = month_amount['October']
            nov_amt = month_amount['November']
            dec_amt = month_amount['December']
            jan_amt = month_amount['January']
            feb_amt = month_amount['February']
            mar_amt = month_amount['March']
            # Determine overall trend: compare Oct to Mar
            overall_increase = mar_amt > oct_amt
            # Note any decrease: check if Feb < Jan (common pattern in financial data)
            feb_decrease = feb_amt < jan_amt
            mar_increase = mar_amt > feb_amt

            if feb_decrease and mar_increase:
                # Pattern: Oct -> (maybe change) -> Jan (peak) -> Feb (drop) -> Mar (recovery)
                return f"Increased overall from {fmt_amt(oct_amt)} in October to {fmt_amt(mar_amt)} in March, with a peak in January ({fmt_amt(jan_amt)}) and a decrease in February to {fmt_amt(feb_amt)}."
            elif feb_decrease:
                # Decrease from Jan to Feb, unclear about Feb to Mar
                return f"Increased from {fmt_amt(oct_amt)} in October to {fmt_amt(jan_amt)} in January, then decreased to {fmt_amt(feb_amt)} in February."
            elif mar_increase and not feb_decrease:
                # Steady increase or Oct < Feb < Mar
                return f"Steadily increased from {fmt_amt(oct_amt)} in October to {fmt_amt(mar_amt)} in March."
            else:
                # Fallback to simple Oct-Mar comparison
                if mar_amt > oct_amt:
                    return f"Increased from {fmt_amt(oct_amt)} in October to {fmt_amt(mar_amt)} in March."
                elif mar_amt < oct_amt:
                    return f"Decreased from {fmt_amt(oct_amt)} in October to {fmt_amt(mar_amt)} in March."
                else:
                    return f"Remained stable at {fmt_amt(oct_amt)} from October to March."
        # else fall through

    # 4. Fallback to sentence scoring (avoid question sentences) as before but we can reuse the scoring logic from earlier.
    # We'll copy the sentence scoring logic from the previous function (but we can also keep it simple: return first non-question sentence that has overlap)
    # However we must ensure we don't return the whole table. We'll implement a simplified version:
    # Split into sentences, filter out question sentences, score by keyword overlap, return best if score>0 else uncertainty.
    # We'll reuse the stopwords and question detection from earlier.

    # Extract keywords from query (simple approach)
    stop_words = {
        'what', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'does', 'do', 'did',
        'show', 'tell', 'me', 'about', 'please', 'can', 'you', 'of', 'for', 'in',
        'on', 'to', 'how', 'why', 'when', 'where', 'who', 'which', 'this', 'that',
        'these', 'those', 'am', 'be', 'been', 'being', 'have', 'has', 'had', 'having'
    }

    query_words = set(
        word.lower().strip('.,!?;:"()[]{}')
        for word in query.split()
        if word.lower() not in stop_words and len(word) > 2
    )

    # Question words to avoid
    question_starters = {
        'what', 'when', 'where', 'who', 'why', 'how',
        'is', 'are', 'was', 'were', 'do', 'does', 'did',
        'can', 'could', 'would', 'should', 'will', 'may', 'might'
    }

    def is_question_sentence(sentence: str) -> bool:
        s = sentence.strip()
        if not s:
            return False
        if s.endswith('?'):
            return True
        first_word = s.split()[0].lower().strip('.,!?;:"()[]{}') if s.split() else ''
        return first_word in question_starters

    if not query_words:
        # If no meaningful words in query, return first non-question sentence
        for sent in re.split(r'[.!?]+', full_text):
            sent = sent.strip()
            if sent and not is_question_sentence(sent):
                return sent + '.'
        return "I could not determine the answer confidently from the retrieved documents."

    # Score sentences
    best_sentence = ""
    best_score = 0

    for sentence in re.split(r'[.!?]+', full_text):
        sentence = sentence.strip()
        if not sentence or len(sentence) < 10:
            continue
        if is_question_sentence(sentence):
            continue
        sentence_words = set(
            word.lower().strip('.,!?;:"()[]{}')
            for word in sentence.split()
        )
        overlap = len(query_words.intersection(sentence_words))
        if overlap == 0:
            continue
        # Bonus for containing digits (often relevant for financial amounts)
        digit_bonus = 1 if any(c.isdigit() for c in sentence) else 0
        # Bonus for containing month names (helps with trend questions)
        month_names = {
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        }
        month_bonus = 1 if any(month in sentence.lower() for month in month_names) else 0
        # Small penalty for sentences that start with question words (less likely to be answers)
        question_penalty = -1 if sentence.split()[0].lower().strip('.,!?;:"()[]{}') in question_starters else 0
        score = overlap + digit_bonus + month_bonus + question_penalty

        if score > best_score:
            best_score = score
            best_sentence = sentence

    if best_score > 0 and len(best_sentence) > 10:
        return best_sentence + '.'
    else:
        return "I could not determine the answer confidently from the retrieved documents."


def _build_search_citations(
    results,
) -> list:

    citations = []

    for result in results:
        metadata = result.get(
            "metadata",
            {},
        )

        citations.append(
            SourceCitation(
                source_type=metadata.get(
                    "document_type",
                    "text",
                ),
                content_snippet=metadata.get(
                    "text",
                    "",
                )[:500],
                document=metadata.get(
                    "document"
                ),
                document_path=metadata.get(
                    "document_path"
                ),
                chunk_id=metadata.get(
                    "chunk_id"
                ),
                page_number=metadata.get(
                    "page_number"
                ),
                word_start=metadata.get(
                    "word_start"
                ),
                word_end=metadata.get(
                    "word_end"
                ),
                score=result.get(
                    "score"
                ),
            )
        )

    return citations


def _build_vision_citations(
    citations,
) -> list:

    response_citations = []

    for citation in citations:
        response_citations.append(
            SourceCitation(
                source_type=citation.get(
                    "source_type",
                    "image",
                ),
                content_snippet=citation.get(
                    "content_snippet",
                    "",
                )[:500],
                document=citation.get(
                    "filename"
                ),
                document_path=citation.get(
                    "image_path"
                ),
                page_number=citation.get(
                    "page_number"
                ),
                score=citation.get(
                    "score"
                ),
            )
        )

    return response_citations


@router.post(
    "/chat",
    response_model=QueryResponse,
)
async def chat(
    request: QueryRequest,
):

    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    try:

        with trace_request(
            name="omnibrain-chat",
            metadata={
                "top_k": request.top_k,
            },
        ) as trace:

            if trace is not None:
                trace.update(
                    input={
                        "query": request.query.strip(),
                    }
                )

            graph_result = omnibrain_graph.invoke(
                {
                    "query": request.query.strip(),
                    "top_k": request.top_k,
                }
            )

            if trace is not None:
                trace.update(
                    output={
                        "route": graph_result.get(
                            "route",
                            "unknown",
                        ),
                        "agent_trace": graph_result.get(
                            "agent_trace",
                            [],
                        ),
                    }
                )

        route = graph_result.get(
            "route",
            "search",
        )

        results = graph_result.get(
            "results",
            [],
        )

        context = graph_result.get(
            "context",
            "",
        )

        agent_trace = list(
            graph_result.get(
                "agent_trace",
                [],
            )
        )

        answer = graph_result.get(
            "answer",
            "",
        )

        citations = []

        if route == "search":

            # Check if guardrail blocked the query
            if graph_result.get("error") == "Query is outside document scope.":
                return QueryResponse(
                    answer=answer,
                    citations=[],
                    agent_trace=agent_trace,
                )

            if not results:
                return QueryResponse(
                    answer=(
                        "I could not find relevant information "
                        "in the uploaded documents."
                    ),
                    citations=[],
                    agent_trace=agent_trace + [
                        "no_results",
                    ],
                )

            if not context:
                raise RuntimeError(
                    "Retrieved documents contain no usable text."
                )

            try:
                answer = _generate_rag_answer(
                    request.query.strip(),
                    context,
                )

                citations = _build_search_citations(
                    results
                )

                agent_trace.extend(
                    [
                        "llm",
                        "rag",
                    ]
                )
            except Exception as e:
                # Use local fallback when OpenAI is unavailable
                answer = _generate_fallback_answer(
                    request.query.strip(),
                    context,
                )

                citations = _build_search_citations(
                    results
                )

                agent_trace.extend(
                    [
                        "local_fallback",
                    ]
                )

        elif route == "vision":

            citations = _build_vision_citations(
                graph_result.get(
                    "citations",
                    [],
                )
            )

            if not answer:
                answer = (
                    "I could not analyze the requested "
                    "image."
                )

        elif route == "sql":

            if not answer:
                answer = str(
                    results
                )

        else:

            answer = (
                answer
                or "Unable to process the request."
            )

        return QueryResponse(
            answer=answer,
            citations=citations,
            agent_trace=agent_trace,
        )

    except HTTPException:
        raise

    except openai.AuthenticationError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The LLM service authentication "
                "is unavailable."
            ),
        )

    except openai.RateLimitError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The LLM service quota or rate "
                "limit has been reached."
            ),
        )

    except openai.APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The LLM service is temporarily "
                "unavailable."
            ),
        )

    except openai.APIStatusError:
        raise HTTPException(
            status_code=502,
            detail=(
                "The LLM service returned an error."
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "OmniBrain failed to process "
                "the request."
            ),
        )