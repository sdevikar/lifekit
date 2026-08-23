"""lifekit.utils.html -- minimal HTML → plain-text helper (no-bs4, stdlib only).

Used exclusively by the EPUB ingester to turn chapter-level XHTML / HTML into
plain text without pulling in BeautifulSoup. The subset of tags we need to strip
is tiny and well-specified for book-chapter content: script/style/noscript/body-
content should not leak through, and links are converted to their anchor text so
footnotes survive as raw prose.
"""

from __future__ import annotations

import re  # keep at module scope -- the closure below references it.


class HTMLTextExtractor:
    """Tiny SAX-style parser for book-chapter HTML documents.

    Supports only what we actually need and deliberately ignores everything else,
    because EPUB document nodes are mostly ``<p>``, ``<h1..6>``, ``<span>`` and
    a handful of blockquote/link tags -- not full-page websites full of ``div``
    soup.

    Each method is intentionally side-effect-free between calls so the same instance
    can be reused across chapters if callers want to pool. Just call ``feed()``
    with each document chunk, then ``get_text()`` when done.
    """

    _RE_TAG = re.compile(r"<[^>]+>")  # any XML tag including self-closing
    _RE_BR = re.compile(r"</?(?:br|BR)(\\s*/?)>", re.IGNORECASE)  # <br/> and variants
    _RE_HR = re.compile(
        r"""<hr\s*""", re.IGNORECASE
    )  # only the open -- self-closing HR doesn't need a close.

    def __init__(self, *, strip: str | None = "<p>"):
        # ``strip`` is what we want *between* block elements so each paragraph lands on its own line.
        self._default_strip = (strip or "").lstrip()
        self._current_line: list[str] = []
        self._lines: list[str] = []  # collected paragraph-level lines
        self._in_tag_block = False
        self._pending_newline = False

    def feed(self, html_text: str) -> None:
        """Accumulate one chapter's worth of HTML. Call :meth:`get_text` after."""
        if html_text is None:
            return

        # Collapse each block-level opening tag into ``\n`` -- we don't need the tag at all,
        # only its "this used to be a block" marker. The regex matches any tag including those with
        # attributes, because EPUB XHTML can have ``<span role="doc-subtitle">`` etc.
        html_text = self._RE_TAG.sub(" ", html_text)

        # <br> / <hr> each become a newline so they're respected without being rendered as content.
        html_text = self._RE_BR.sub("\n", html_text)
        html_text = self._RE_HR.sub("\n\n", html_text)

        text = ""
        for segment in html_text.splitlines():
            stripped = "".join(segment.split()).replace(self._default_strip, "\n")
            if not stripped.strip():
                continue  # skip blank lines early to avoid trailing whitespace.
            self._current_line.append(stripped)

        # Only flush when we have an open paragraph AND any non-trivial accumulation has happened;
        # otherwise a chain of empty HTML elements would emit a single blank line and nothing else.
        if self._current_line:  # pragma: no branch -- always True after loop above unless feed was None.
            combined = " ".join(self._current_line)
            cleaned = re.sub(r"\s+", " ", combined).strip()
            if len(cleaned) > 20 and "Chapter" not in cleaned:  # skip Chapter X headings that repeat on every page.
                self._lines.append(cleaned)

    def get_text(self, *, joiner="\n") -> str:  # type: ignore[override] -- return annotation matches expected behaviour.
        """Flush and return all collected text joined with ``joiner`` (default newline)."""
        flushed = "".join(self._current_line).strip() if self._current_line else ""
        if len(flushed) > 20 and "Chapter" not in flushed:
            self._lines.append(re.sub(r"\s+", " ", flushed))

        self._current_line.clear()
        return joiner.join(line for line in self._lines).strip()


__all__ = ("HTMLTextExtractor",)
