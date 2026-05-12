# SafeAbroad Agent

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-App-009688)
![Safety](https://img.shields.io/badge/Safety-Trauma--Informed-green)
![Privacy](https://img.shields.io/badge/Privacy-Local--First-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

A trauma-informed, privacy-first emergency documentation agent for international students overseas.

SafeAbroad Agent helps Chinese-speaking international students document assault, street violence, threats, injuries, property loss, and follow-up needs in a structured way. It turns Chinese recall into a careful bilingual case record, keeps uncertainty visible, and drafts neutral English materials that users can review before sharing with police, doctors, universities, insurers, victim support services, or consulates.

## Why This Project Exists

After an assault or frightening incident abroad, international students may face language barriers, unfamiliar legal systems, insurance confusion, and psychological shock. Many users need help organizing facts without being pressured, led, or encouraged to exaggerate.

SafeAbroad Agent focuses on documentation, evidence preservation, and communication preparation. It is not a replacement for emergency services, lawyers, doctors, counsellors, or university support staff.

## What It Can Do

- Immediate safety triage in Chinese
- Trauma-informed incident intake
- Chronological timeline reconstruction
- Follow-up questioning for missing details and logical conflicts
- Editable timeline with uncertainty markers
- Evidence and injury checklist with collection guidance
- Chinese-to-English police-style statement generation
- Medical, university, police follow-up, insurance, and victim-support drafts
- Jurisdiction-aware support-resource suggestions
- Local-first API-key settings for Qwen, OpenAI, Anthropic, or OpenAI-compatible providers

## What It Does Not Do

- It does not replace police, lawyers, doctors, counsellors, or emergency services.
- It does not provide legal, medical, immigration, or psychological advice.
- It does not tell users whether a suspect is guilty.
- It does not predict exact criminal sentences or court outcomes.
- It does not fabricate, exaggerate, or “clean up” uncertain memories into confirmed facts.
- It does not encourage retaliation, confrontation, or unsafe evidence collection.

## Demo Flow

User input:

> 我昨晚在便利店外被一个陌生人推了一下，他还抢了我的薯条。我很害怕，记不太清顺序。

Agent follow-up:

> 先不用急着把所有细节说完整。我们一步一步来。你最先注意到对方是在便利店里面、门口，还是外面街上？

Generated police-style statement:

> On the evening of [date], I was outside a convenience store when an unknown person approached me. I remember being pushed and feeling frightened. I am not fully certain of the exact sequence, but I recall that the person took my fries and made threatening remarks...

The example intentionally preserves uncertainty instead of turning unclear memory into a stronger claim.

## Architecture

```text
safeabroad-agent/
├── backend/
│   ├── agents/            # deterministic agent modules
│   ├── models/            # Pydantic case state
│   ├── prompts/           # runtime prompt templates
│   ├── services/          # workflow orchestration and LLM adapter
│   ├── static/            # Chinese web UI
│   └── tests/             # Python safety and workflow tests
├── lib/
│   ├── agent/             # TypeScript reference contracts
│   ├── prompts/           # public prompt-design docs
│   ├── safety/            # safety-boundary constants
│   └── schemas/           # Zod schemas for incident data contracts
├── tests/                 # TypeScript reference tests
├── docs/                  # architecture, modules, safety, roadmap
└── examples/              # sample case and CLI demo
```

The current runnable app is a FastAPI backend with a static browser UI. The TypeScript `lib/` layer documents stable agent contracts and schemas for future SDK, Next.js, or PWA implementations.

## Quick Start

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002
```

Open:

```text
http://127.0.0.1:8002/
```

API docs:

```text
http://127.0.0.1:8002/docs
```

## Configure an LLM Provider

The app can run with deterministic fallback logic, but LLM calls improve timeline extraction and wording.

Create `.env` locally:

```powershell
Copy-Item .env.example .env
```

Example Qwen-compatible settings:

```text
LLM_PROVIDER=qwen
DASHSCOPE_API_KEY=your-dashscope-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
```

Never commit `.env` or API keys. The web UI also includes a local API settings modal for Qwen, OpenAI, Anthropic, and custom OpenAI-compatible endpoints.

## Run Tests

Python workflow tests:

```powershell
python -m pytest backend/tests
```

TypeScript reference tests:

```powershell
npm install
npm test
```

## Screenshots

Screenshots are stored in `docs/screenshots/` when generated from the local demo UI.

Recommended captures:

- Emergency triage
- Incident intake
- Timeline builder
- Evidence checklist
- English statement preview

## Roadmap

- [x] Incident intake workflow
- [x] Timeline reconstruction
- [x] Follow-up interview loop
- [x] Evidence checklist and preservation guidance
- [x] English police-style statement draft
- [x] Medical, university, police follow-up, and support drafts
- [x] API settings for multiple LLM providers
- [ ] PDF export
- [ ] Offline encrypted storage
- [ ] Mobile PWA mode
- [ ] Broader jurisdiction-aware support resources
- [ ] Multi-language support beyond Chinese and English

## Professional GitHub Checklist

- [x] README explains the problem quickly
- [x] README includes features and limitations
- [x] Safety boundaries are documented
- [x] Privacy policy is included
- [x] Security policy is included
- [x] Agent specification is included
- [x] Prompt files are version-controlled
- [x] Pydantic and Zod schemas exist
- [x] Python workflow tests exist
- [x] TypeScript reference tests exist
- [x] Example user flow is shown
- [x] License and contribution guide are included
- [x] `.env` and secrets are ignored

## License

MIT. See [LICENSE](LICENSE).
