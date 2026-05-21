# Prompt Design

SafeAbroad prompts are designed around trauma-informed documentation rather than interrogation.

## Principles

- Ask one question at a time
- Start from open recall
- Avoid suggesting facts
- Preserve uncertainty
- Keep Chinese user language visible
- Generate English only when useful
- Separate confirmed facts, uncertain memories, assumptions, emotions, and missing details

## Runtime Prompts

Runtime prompt templates live in `backend/prompts/`.

Public prompt-design references live in `lib/prompts/`.

## Safety Expectations

Every prompt should include explicit constraints against:

- Legal advice
- Medical diagnosis
- Fact fabrication
- Exact sentencing prediction
- Confrontation advice
- Pressure to report

## Evaluation Examples

Good follow-up:

> 你记得这句话是在对方碰到你之前还是之后吗？如果记不清，也可以说明只是不确定先后顺序。

Bad follow-up:

> 所以他先威胁你，然后故意攻击你，对吗？

The bad version suggests intent and sequence that the user may not have stated.
