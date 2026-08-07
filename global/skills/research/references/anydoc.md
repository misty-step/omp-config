# anydoc

Local document → GitHub-Flavored Markdown. Built by Firecrawl. No API key.

Use when a task needs the text of an office file, spreadsheet, presentation,
ebook, or PDF that agents cannot read as plain text.

## Install

Workstation CLI (already preferred path):

```bash
npm install -g @firecrawl/anydoc
anydoc --version
```

One-shot without global install:

```bash
npx -y @firecrawl/anydoc report.docx
```

Libraries when embedding in code:

- Node: `@firecrawl/anydoc`
- Python: `firecrawl-anydoc`
- Rust: `anydoc` crate

## CLI

```bash
anydoc report.docx                 # Markdown on stdout
anydoc slides.pptx -o slides.md    # write a file
anydoc - --format csv < data.csv   # stdin; name CSV format
curl -sL https://example.com/a.pdf | anydoc -
```

Supported inputs: `.doc`, `.docx`, `.docm`, `.odt`, `.rtf`, `.epub`, `.pdf`,
`.ppt`, `.pps`, `.pot`, `.pptx`, `.pptm`, `.ppsx`, `.ppsm`, `.odp`, `.xls`,
`.xlsx`, `.xlsm`, `.xlsb`, `.ods`, `.csv`.

Exit codes: `0` success, `1` conversion failure, `2` usage error.

## Rules

1. Prefer anydoc over guessing at binary office formats with `read` or `strings`.
2. Detect format from content. Pass `--format` only for CSV-on-stdin or a wrong extension.
3. For a large document, write `-o file.md` and read only the needed sections.
4. Scanned or image-only PDFs need OCR. anydoc fails those on purpose. Escalate to hosted Firecrawl Parse only when the operator wants cloud OCR (`Authorization: Bearer __mint.firecrawl.default__` against the Parse API). Do not send private docs to Parse without approval.
5. anydoc is local acquisition. It is not a web crawler and not a substitute for Exa or Firecrawl scrape.

## Research fit

| Need | Tool |
|---|---|
| Local `.docx` / `.pdf` / `.xlsx` text | `anydoc` |
| Web page text | Firecrawl scrape |
| Find sources | Exa |
| Dynamic web UI | browser / agent-browser |
