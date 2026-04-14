# Anthropic (Claude) prompting

- Claude responds well to XML-style section tags (e.g. `<instructions>`, `<examples>`) for long prompts.
- Put the most important constraints at the top and repeat critical safety rules if needed.
- Use markdown headings for structure; avoid walls of unstructured text.
- When using extended thinking, separate chain-of-thought from the final user-visible answer in the target agent's prompt design.
- For long static instructions, structure content so it can benefit from prompt caching (stable prefixes, variable suffixes).
