# Project instructions for future chats

Project 042: **Document Intelligence for Application Readiness and Missing-Requirement Detection**.

1. Read `HANDOFF.md`, `PROJECT_BRIEF.md`, `TEAM_CONTRACT.md`, and the requested personal/merge handoff before work. The former sequential S01–S10 plan is superseded; use SG/JB/M identifiers.
2. **Sakshi Gupta** owns `SAKSHI_HANDOFF.md` (SG sprints). **Jigisha Baiswar** owns `JIGISHA_HANDOFF.md` (JB sprints). `MERGE_HANDOFF.md` governs shared setup/merges; Sakshi is integration lead. File ownership is in the master handoff.
3. A path-only request means execute the next eligible sprint for that handoff. One sprint/checkpoint per chat. Resume unfinished work, verify it, update its handoff and stop. Do not ask the student to repeat the idea.
4. If given only the master handoff, execute its next eligible M checkpoint. If a merge is waiting for personal work, report the exact missing sprint and its path; do not guess which person the user is.
5. M00 creates the common baseline and separate branches/checkouts. Never run concurrent branch switches in the same directory. After M00, work in the selected owner's checkout and update that checkout's handoff.
6. During parallel work each agent edits only its owner's files/handoff/notes. Do not edit `HANDOFF.md`, `MERGE_HANDOFF.md`, `TEAM_CONTRACT.md`, `requirements.txt`, or peer files. Record requests locally; the merge chat reconciles shared files.
7. Personal handoffs are the live source for their tracks; master status is a merge-time snapshot. Check actual branch/worktree evidence before claiming prerequisites passed or changes were merged. Keep DONE and merged status distinct.
8. Teach before coding in simple English, write complete executable files, explain key functions, and test each checkpoint. Run available commands yourself. If only the student can perform a step, give the exact action and wait for their result.
9. Preserve student edits and working code. Use simple local Python, OpenCV, NumPy, Matplotlib, Pillow, Pytesseract/Tesseract and Streamlit. No ML training, LLM APIs, cloud, database, auth or extra backend.
10. Honor `TEAM_CONTRACT.md` public APIs. Test fixtures/stubs are development-only and must be removed from the production flow at M01. Never report fixture success as real OCR or end-to-end success.
11. Update the selected handoff at start, checkpoints, blockers and before ending. Record commands, real results, artifacts, branch/path, remaining work and exact next action. Never fabricate data, metrics, screenshots, references or completed reviews.
12. Use labeled fictional/reusable samples; protect private uploads. Readiness concerns configured presence and usable information, not authenticity or official eligibility. Do not push/publish/send unless requested.
13. M00 foundation evidence is in `docs/merge/M00.md`; inspect actual Git/worktree and environment evidence before assuming setup or later application work is complete. M00 does not implement application modules or personal sprints.

14. Latest user Git policy (2026-11-10): automatically create a local commit after each verified SG/JB sprint and M checkpoint, using a one-line explanation. Keep all further commits local until both SG01–SG06 and JB01–JB06 and final M03 are complete and verified. Preserve the already-published SG01 history; do not undo it. Combine both owners' contributions through the existing M01/M02/M03 gates, preserving their authorship; do not merge incomplete tracks early or push intermediate work. Update `main` with the combined project only after all sprints and M03 verification are finished.
15. Use the correct owner's Git author for local sprint commits. Linked worktrees must use worktree-specific identity settings; never change the shared/global author to switch people. A local commit does not require signing in to GitHub.
