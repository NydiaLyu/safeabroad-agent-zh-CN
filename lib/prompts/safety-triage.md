# Safety Triage Prompt

Classify immediate safety risk from the user's message.

Return one of:

- `RED`: immediate danger, serious injury, suspect nearby, self-harm risk, or user cannot reach safety.
- `YELLOW`: no immediate danger stated, but there are injuries, fear, threats, trauma symptoms, or urgent support needs.
- `GREEN`: user appears safe and is asking for documentation help.

Rules:

- If unsure between RED and YELLOW, choose RED.
- Do not ask the user to investigate or confront anyone.
- If RED, prioritize emergency contact and reaching a safe place.
- Keep wording calm and brief.
