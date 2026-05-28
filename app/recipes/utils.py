"""Utility functions for recipe operations."""

import re


class ReStr(str):
    """Subclass of `str` that adds a method wrapping re.sub for better syntax"""

    def sub(self, pattern: str, repl: str, count: int = 0, flags: int | re.RegexFlag = 0) -> "ReStr":
        """Wrapper for `re.sub` with the same parameters, with the string to search through renamed to `self`"""

        return ReStr(re.sub(pattern, repl, self, count, flags))


def slugify(text: str) -> str:
    """Convert text to a normalized slug with underscores.

    Replaces runs of non-alphanumeric characters with underscores,
    then trims leading/trailing underscores for a clean result.
    """
    slug = (ReStr(text.lower())
            .sub(r"[^a-z0-9]+", "_")  # replace non-alphanumeric characters
            .sub("^_+|_+$", ""))  # strip underscores
    return str(slug)

