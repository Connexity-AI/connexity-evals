# OpenAI prompting

- Prefer markdown structure with clear headings and bullet lists for long system prompts.
- When using JSON or strict formats, specify the schema explicitly and give a minimal valid example.
- If the target stack uses developer vs system messages, keep immutable policy in system and task-specific details in developer where appropriate.
- For tool use, describe when to call each tool and what to do if tools fail or return empty results.
- Avoid contradictory instructions; later sections should refine, not override, earlier hard constraints without signaling the change.
