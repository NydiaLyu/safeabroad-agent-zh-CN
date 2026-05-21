# SafeAbroad Agent 平安海外 智能体助手

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-App-009688)
![Safety](https://img.shields.io/badge/Safety-Trauma--Informed-green)
![Privacy](https://img.shields.io/badge/Privacy-Local--First-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

A trauma-informed, privacy-first emergency documentation agent for international students overseas.

秉持创伤关怀理念、以隐私保护为首要原则，面向海外留学生打造的紧急情况记录智能助手。

SafeAbroad Agent helps Chinese-speaking international students document assault, street violence, threats, injuries, property loss, and follow-up needs in a structured way. It turns Chinese recall into a careful bilingual case record, keeps uncertainty visible, and drafts neutral English materials that users can review before sharing with police, doctors, universities, insurers, victim support services, or consulates.

该智能体助手可以帮助中文留学生，条理清晰地记录袭击事件、街头暴力、人身威胁、身体受伤、财产损失以及后续诉求。该工具能将当事人的中文陈述整理成严谨的双语事件记录，清晰标注存疑信息，并撰写客观中立的英文文书，用户可先行核对确认，再提交给警方、医护人员、院校、保险公司、受害者援助机构以及领事馆等相关方。

## Why This Project Exists 项目成立的初衷

After an assault or frightening incident abroad, international students may face language barriers, unfamiliar legal systems, insurance confusion, and psychological shock. Many users need help organizing facts without being pressured, led, or encouraged to exaggerate.

在境外遭遇袭击或令人恐惧的事件后，留学生往往会面临语言不通、不熟悉当地法律体系、索赔困境和心理冲击等问题，需要在不会受到施压、诱导的情况下梳理事件实情，且不会夸大事实。

SafeAbroad Agent focuses on documentation, evidence preservation, and communication preparation. It is not a replacement for emergency services, lawyers, doctors, counsellors, or university support staff.

该智能助手专注于文书整理、证据留存以及沟通事宜筹备。它无法替代应急救援机构、律师、医生、心理咨询师以及校方工作人员。

## What It Can Do 它能做什么

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

- 用中文对安全风险等级进行研判
- 结合创伤心理视角的事件信息录入
- 按时间顺序还原事件完整经过
- 针对缺失细节与逻辑矛盾开展跟进问询
- 可编辑且标注存疑信息的时间线
- 附带采集指引的证据与伤情核对清单
- 生成中英双语类似警方笔录的陈述
- 撰写医疗对接、校方沟通、警方跟进、保险理赔及受害者帮扶等各类文书草案
- 结合属地管辖规则推荐对应的帮扶资源
- 本地优先API密钥配置（通义千问、OpenAI、Anthropic及各类兼容OpenAI接口服务商）

## What It Does Not Do 它不能做什么

- It does not replace police, lawyers, doctors, counsellors, or emergency services.
- It does not provide legal, medical, immigration, or psychological advice.
- It does not tell users whether a suspect is guilty.
- It does not predict exact criminal sentences or court outcomes.
- It does not fabricate, exaggerate, or “clean up” uncertain memories into confirmed facts.
- It does not encourage retaliation, confrontation, or unsafe evidence collection.

- 它无法替代警察、律师、医生、心理咨询师以及各类应急服务机构。
- 它不提供法律、医疗、移民以及心理辅导意见。
- 它无法判定嫌疑人是否有罪。
- 它不能精准预判刑事判决与法庭审判结果。
- 它不会编造、夸大内容，也不会将模糊不清的记忆梳理篡改成为已被确认的事实。
- 它不怂恿他人实施报复行为、正面冲突，也不引导用户采取不安全的取证方式。
  
## Demo Flow 使用示例

User input 用户输入:

> 我昨晚在便利店外被一个陌生人推了一下，他还抢了我的薯条。我很害怕，记不太清顺序。

Agent follow-up 智能体反馈:

> 先不用急着把所有细节说完整。我们一步一步来。你最先注意到对方是在便利店里面、门口，还是外面街上？

Generated police-style statement 生成警方笔录式陈述:

> On the evening of [date], I was outside a convenience store when an unknown person approached me. I remember being pushed and feeling frightened. I am not fully certain of the exact sequence, but I recall that the person took my fries and made threatening remarks...

The example intentionally preserves uncertainty instead of turning unclear memory into a stronger claim.

该示例刻意保留不确定表述，而非将模糊的记忆转化为笃定的断言。

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
