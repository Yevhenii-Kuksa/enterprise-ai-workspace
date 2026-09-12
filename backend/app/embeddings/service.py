from app.embeddings.provider import EmbeddingProvider, EmbeddingResult


def generate_embeddings(
    provider: EmbeddingProvider,
    texts: list[str],
) -> list[EmbeddingResult]:
    if not texts:
        return []

    vectors = provider.embed_texts(texts)

    if len(vectors) != len(texts):
        raise ValueError(
            "Embedding provider returned a different number of vectors than texts."
        )

    results: list[EmbeddingResult] = []

    for vector in vectors:
        if len(vector) != provider.dimensions:
            raise ValueError(
                "Embedding vector dimensions do not match provider dimensions."
            )

        results.append(
            EmbeddingResult(
                model_name=provider.model_name,
                dimensions=provider.dimensions,
                vector=vector,
            )
        )

    return results