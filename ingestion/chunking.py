from typing import List, Dict


class TextChunker:

    def __init__(self, chunk_size: int = 200, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[Dict]:

        if not text.strip():
            return []

        words = text.split()

        chunks = []
        chunk_id = 1

        step = self.chunk_size - self.overlap

        if step <= 0:
            raise ValueError("chunk_size must be greater than overlap")

        for start in range(0, len(words), step):

            chunk_words = words[start:start + self.chunk_size]

            if not chunk_words:
                break

            chunks.append({
                "chunk_id": chunk_id,
                "text": " ".join(chunk_words),
                "word_start": start,
                "word_end": start + len(chunk_words)
            })

            chunk_id += 1

        return chunks


if __name__ == "__main__":

    sample_text = (
        "OmniBrain is an AI-powered document understanding platform. "
        * 30
    )

    chunker = TextChunker(
        chunk_size=20,
        overlap=5
    )

    chunks = chunker.chunk_text(sample_text)

    print(f"Total Chunks: {len(chunks)}\n")

    for chunk in chunks:
        print(chunk)
        print("-" * 50)