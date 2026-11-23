---
name: stage
description: Run one stage of the course build plan in spec/11 (Stages 0-4 and 6-9). Use when the owner types /stage followed by a stage number.
argument-hint: "[stage number 0-9]"
disable-model-invocation: true
---

Run **Stage $0** of the build plan in `spec/11-build-plan-and-prompts.md`. If no stage number came with the command, read `BUILD_LOG.md`, name the next stage and ask me to confirm it. Anything typed after the stage number (all arguments: "$ARGUMENTS") fills the stage prompt's placeholders, such as the module in Stage 6's `<M21>`; if a placeholder is still open, ask me.

1. Read `BUILD_LOG.md` and `course.json` if they exist and summarise in three lines where the build stands. If an earlier stage isn't done, say so and stop.
2. Read the Stage $0 section of spec/11: its **Reads**, its **Done when** and its prompt. Read only the files it lists (CLAUDE.md §3 says where everything is).
3. Carry out that prompt exactly. Where it says to wait for my OK, stop and wait. Stage 5 is the module loop: use `/build-module <module id>` for it.
4. Check the **Done when** list item by item. From Stage 1 on, run `python tools/build.py`, then `python tools/ci.py --partial`, and quote the summary line of every step. Don't call the stage done while anything is red: fix the root cause, or report the failure with its output.
5. Update `BUILD_LOG.md` (the "Current state / Next step" block at the top first), commit with the message `Stage $0: <what was done>`, and report in 5–10 lines, ending with the command that starts the next session's work.
