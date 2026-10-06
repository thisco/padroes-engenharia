"""Padrões de recurso externo em HTML e CSS (R-EXTERNO), compartilhados pelo build e pela regra
R-APRESENTACAO."""

from __future__ import annotations

import re

# `@import url(...)` já cai no padrão de `url(...)`, no CSS e no HTML; o de `@import` pega só a
# forma com aspas, para não contar o mesmo recurso duas vezes.
EXTERNOS = {
    ".html": (
        re.compile(r"<link\b[^>]*\bhref\s*=\s*[\"']?\s*(?:https?:)?//", re.I),
        re.compile(r"<script\b[^>]*\bsrc\s*=\s*[\"']?\s*(?:https?:)?//", re.I),
        re.compile(r"@import\s+[\"']\s*(?:https?:)?//", re.I),
        # Imagem e mídia também são carregadas pelo navegador (um pixel de rastreio vindo do
        # Markdown, por exemplo); `<a href>` fica de fora porque só navega.
        re.compile(
            r"<(?:img|iframe|source|video|audio|track|embed|object|input)\b[^>]*"
            r"\b(?:src|poster|data)\s*=\s*[\"']?\s*(?:https?:)?//",
            re.I,
        ),
        re.compile(r"\bsrcset\s*=\s*[\"'][^\"']*(?:https?:)?//", re.I),
        # `url(...)` em `style="..."` e em `<style>` inline.
        re.compile(r"url\(\s*[\"']?\s*(?:https?:)?//", re.I),
    ),
    ".css": (
        re.compile(r"@import\s+[\"']\s*(?:https?:)?//", re.I),
        re.compile(r"url\(\s*[\"']?\s*(?:https?:)?//", re.I),
    ),
}
