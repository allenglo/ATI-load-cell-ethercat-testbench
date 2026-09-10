# Pitfalls And Guardrails

Pitfall 1: treating subdevice code as host code
- Symptom: heartbeat/LED works but no real ATI query path from LaunchPad.
- Guardrail: confirm master capability first; do not assume role change by small edits.

Pitfall 2: confusing proof-of-concept path with target architecture
- Symptom: host pysoem path becomes permanent and firmware lane stalls.
- Guardrail: keep host pysoem as regression tool only; track firmware milestones separately.

Pitfall 3: noisy logs hiding signal
- Symptom: huge logs with little progress evidence.
- Guardrail: one-line UART output per cycle window and short run lengths.

Pitfall 4: risky edits in known-good demos
- Symptom: current COM10 heartbeat breaks while host lane still not implemented.
- Guardrail: stage host work in isolated subtree first; merge only after milestone checks.

Pitfall 5: handoff gaps
- Symptom: next agent repeats discovery work.
- Guardrail: always leave exact command, expected output snippet, and one blocker note.
