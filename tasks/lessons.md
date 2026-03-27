# Lessons Learned

- When user asks to strictly follow `guidelines.md`, always execute full workflow lifecycle: plan in `tasks/todo.md`, implementation, verification evidence, and final review update.
- Before promising commits, verify whether a git repository exists; if missing, initialize it first and communicate remote-push constraints clearly.
- For repeat phase requests, always add a new phase-specific section in `tasks/todo.md` before coding and map commits explicitly to that phase's todo items.
- When architecture direction changes, update `architecture.md`, `idea.md`, and all `tasks/*` roadmap artifacts in one synchronized pass to avoid stale contradictions.
- If user asks to start implementation after a planning pass, immediately execute code changes and verification in the same turn instead of ending at plan handoff.
