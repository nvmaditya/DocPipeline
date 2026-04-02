# Lessons Learned

- When user asks to strictly follow `guidelines.md`, always execute full workflow lifecycle: plan in `tasks/todo.md`, implementation, verification evidence, and final review update.
- Before promising commits, verify whether a git repository exists; if missing, initialize it first and communicate remote-push constraints clearly.
- For repeat phase requests, always add a new phase-specific section in `tasks/todo.md` before coding and map commits explicitly to that phase's todo items.
- When architecture direction changes, update `architecture.md`, `idea.md`, and all `tasks/*` roadmap artifacts in one synchronized pass to avoid stale contradictions.
- If user asks to start implementation after a planning pass, immediately execute code changes and verification in the same turn instead of ending at plan handoff.
- When the user asks to strictly follow `guidelines.md`, always begin by updating `tasks/todo.md` and `tasks/lessons.md`, then keep one isolated commit per explicit todo item.
- In a dirty worktree, explicitly confirm isolated path-scoped commits before proceeding and avoid touching unrelated files.
- For UX quality complaints, always treat frontend work as production polish: define spacing system, mobile breakpoints, accessibility focus states, and run frontend plus integration tests before marking done.
- When the cmd tool shell does not return output for long-running Python processes, use `view_file` and `list_dir` to monitor file-system changes as a proxy for build progress, and always give the user the exact manual command to run in their own terminal.
- When switching embedding models (e.g., local SentenceTransformer → Ollama), the existing FAISS indexes are incompatible (different vector dimensions) and MUST be deleted and rebuilt. Always use `--force` on the build script after a model change.
- For embedding backends that use the OpenAI SDK (Ollama, GitHub Models), require a dummy env var (OLLAMA_API_KEY=ollama) to be set — document this clearly in scripts and add a preflight check.
