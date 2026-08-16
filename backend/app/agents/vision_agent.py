import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI

from Config.Config import settings
from ingestion.image_index import ImageIndex


class VisionAgent:

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.image_index = ImageIndex()

    @staticmethod
    def _encode_image(image_path: str) -> str:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        mime_type, _ = mimetypes.guess_type(
            str(path)
        )

        if mime_type is None:
            mime_type = "image/png"

        with open(path, "rb") as image_file:
            encoded = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        return (
            f"data:{mime_type};base64,{encoded}"
        )

    def search_images(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:

        return self.image_index.search(
            query=query,
            top_k=top_k,
        )

    def analyze_image(
        self,
        query: str,
        image_path: str,
    ) -> str:

        image_data = self._encode_image(
            image_path
        )

        response = self.client.responses.create(
            model=settings.llm_model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are OmniBrain's Vision Agent. "
                                "Answer the user's question using "
                                "ONLY the provided image. "
                                "Do not invent information. "
                                "If the image does not contain "
                                "enough information, say so clearly.\n\n"
                                f"User question:\n{query}"
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": image_data,
                        },
                    ],
                }
            ],
        )

        answer = response.output_text.strip()

        if not answer:
            raise RuntimeError(
                "Vision model returned an empty response."
            )

        return answer

    def run(
        self,
        query: str,
        top_k: int = 3,
    ) -> Dict[str, Any]:

        if not query or not query.strip():
            raise ValueError(
                "Vision agent query cannot be empty."
            )

        results = self.search_images(
            query=query.strip(),
            top_k=top_k,
        )

        if not results:
            return {
                "answer": (
                    "I could not find a relevant image "
                    "in the uploaded documents."
                ),
                "results": [],
                "citations": [],
                "agent_trace": [
                    "vision_agent",
                    "image_search",
                    "no_results",
                ],
            }

        usable_result = None

        for result in results:
            metadata = result.get(
                "metadata",
                {},
            )

            image_path = metadata.get(
                "path"
            )

            if image_path and Path(
                image_path
            ).exists():
                usable_result = result
                break

        if usable_result is None:
            return {
                "answer": (
                    "A relevant image was found, "
                    "but the image file is not available."
                ),
                "results": results,
                "citations": [],
                "agent_trace": [
                    "vision_agent",
                    "image_search",
                    "image_not_found",
                ],
            }

        metadata = usable_result.get(
            "metadata",
            {}
        )

        answer = self.analyze_image(
            query=query.strip(),
            image_path=metadata["path"],
        )

        citation = {
            "source_type": "image",
            "content_snippet": metadata.get(
                "ocr_text",
                "",
            )[:500],
            "page_number": metadata.get(
                "page"
            ),
            "score": usable_result.get(
                "score"
            ),
            "filename": metadata.get(
                "filename"
            ),
            "image_path": metadata.get(
                "path"
            ),
        }

        return {
            "answer": answer,
            "results": results,
            "citations": [citation],
            "agent_trace": [
                "vision_agent",
                "image_search",
                "vlm",
            ],
        }


def run_vision_agent(
    query: str,
    top_k: int = 3,
) -> Dict[str, Any]:

    agent = VisionAgent()

    try:
        return agent.run(
            query=query,
            top_k=top_k,
        )
    finally:
        agent.image_index.close()