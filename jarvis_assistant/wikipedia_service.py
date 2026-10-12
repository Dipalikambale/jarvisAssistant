import logging

logger = logging.getLogger(__name__)


def summarize(query: str, sentences: int = 2) -> str:
    import wikipedia

    try:
        return wikipedia.summary(query, sentences=sentences, auto_suggest=True)
    except wikipedia.exceptions.DisambiguationError as error:
        options = ", ".join(error.options[:5])
        raise ValueError(
            f"That topic is ambiguous. Try a more specific search, such as: {options}"
        ) from error
    except wikipedia.exceptions.PageError as error:
        raise ValueError(f"I couldn't find a Wikipedia article for '{query}'.") from error
    except wikipedia.exceptions.WikipediaException as error:
        logger.exception("Wikipedia lookup failed", extra={"event": "wikipedia_error"})
        raise RuntimeError("Wikipedia is unavailable right now. Try again later.") from error
