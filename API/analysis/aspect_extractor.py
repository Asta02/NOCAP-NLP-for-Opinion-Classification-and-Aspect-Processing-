"""
=========================================================
Aspect Extractor
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Rule-based aspect extraction.

This module identifies predefined HR-related
aspects and extracts a local phrase around
each detected aspect.

Future versions may replace this implementation
with embeddings or LLMs without changing the
public API.
"""

from __future__ import annotations

import re

from .constants import (
    ASPECT_KEYWORDS,
    DEFAULT_CONTEXT_WINDOW,
)

from .schemas import (
    ExtractedAspect,
)


# =====================================================
# ASPECT EXTRACTOR
# =====================================================


class AspectExtractor:
    """
    Rule-based aspect extractor.
    """

    def __init__(
        self,
        context_window: int = DEFAULT_CONTEXT_WINDOW,
    ) -> None:
        """
        Initialize regex patterns.
        """

        self.context_window = context_window

        self.patterns: dict[
            str,
            re.Pattern[str],
        ] = {}

        for (
            aspect,
            keywords,
        ) in ASPECT_KEYWORDS.items():

            pattern = (
                r"\b("
                + "|".join(
                    map(
                        re.escape,
                        sorted(
                            keywords,
                            key=len,
                            reverse=True,
                        ),
                    )
                )
                + r")\b"
            )

            self.patterns[
                aspect
            ] = re.compile(
                pattern,
                flags=re.IGNORECASE,
            )

    # =================================================
    # PRIVATE HELPERS
    # =================================================

    def _find_clause(
        self,
        review: str,
        match: re.Match[str],
    ) -> str:
        """
        Return the clause containing
        the matched keyword.
        """

        separators = re.compile(
            (
                r"\bbut\b|"
                r"\bhowever\b|"
                r"\balthough\b|"
                r"\bthough\b|"
                r"[.!?]"
            ),
            flags=re.IGNORECASE,
        )

        start = 0

        for separator in separators.finditer(
            review
        ):

            if (
                separator.end()
                <= match.start()
            ):

                start = separator.end()

            elif (
                separator.start()
                >= match.end()
            ):

                end = separator.start()

                return review[
                    start:end
                ].strip()

        return review[start:].strip()

    def _extract_phrase(
        self,
        clause: str,
        match: re.Match[str],
    ) -> str:
        """
        Extract a small phrase around
        the detected aspect.
        """

        words = clause.split()

        keyword = (
            match.group(0)
            .lower()
        )

        keyword_index = None

        for (
            index,
            word,
        ) in enumerate(words):

            cleaned = re.sub(
                r"[^\w-]",
                "",
                word.lower(),
            )

            if cleaned == keyword:

                keyword_index = index
                break

        if keyword_index is None:

            return clause

        start = max(
            0,
            keyword_index
            - self.context_window,
        )

        end = min(
            len(words),
            keyword_index
            + self.context_window
            + 1,
        )

        return " ".join(
            words[start:end]
        )

    # =================================================
    # PUBLIC API
    # =================================================

    def extract(
        self,
        text: str,
    ) -> list[ExtractedAspect]:
        """
        Extract aspects and their
        local phrases from a review.
        """

        review = text.strip()

        if not review:
            return []

        results: list[
            ExtractedAspect
        ] = []

        for (
            aspect,
            pattern,
        ) in self.patterns.items():

            for match in pattern.finditer(
                review
            ):

                clause = self._find_clause(
                    review,
                    match,
                )

                local_match = pattern.search(
                    clause
                )

                if local_match is None:
                    continue

                phrase = (
                    self._extract_phrase(
                        clause,
                        local_match,
                    )
                )

                results.append(
                    ExtractedAspect(
                        aspect=aspect,
                        phrase=phrase,
                    )
                )

        return results


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Interactive CLI.
    """

    extractor = AspectExtractor()

    print("=" * 60)
    print("Aspect Extractor")
    print("=" * 60)
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        review = input(
            "\nEnter review:\n> "
        ).strip()

        if review.lower() in {
            "exit",
            "quit",
            "q",
        }:
            print("\nGoodbye!")
            break

        try:

            aspects = extractor.extract(
                review
            )

            print()

            if not aspects:

                print(
                    "No aspects detected."
                )

                continue

            print("=" * 60)
            print("Detected Aspects")
            print("=" * 60)

            for aspect in aspects:

                print(
                    aspect.model_dump_json(
                        indent=4,
                    )
                )

            print("=" * 60)

        except KeyboardInterrupt:

            print("\n\nGoodbye!")
            break

        except Exception as error:

            print(
                f"\nError: {error}"
            )


if __name__ == "__main__":
    main()