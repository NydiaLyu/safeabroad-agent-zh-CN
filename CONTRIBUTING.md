# Contributing

Thank you for helping improve SafeAbroad Agent.

## Development Setup

```powershell
python -m pip install -r requirements.txt
python -m pytest backend/tests
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002
```

Optional TypeScript reference checks:

```powershell
npm install
npm test
```

## Contribution Priorities

- Improve safety boundaries
- Improve trauma-informed questioning
- Improve privacy and redaction
- Add jurisdiction-aware official support resources
- Add tests for non-fabrication and uncertainty preservation
- Improve accessibility and Chinese UX

## Commit Style

Use clear conventional commits:

- `feat: add incident intake schema`
- `feat: implement trauma-informed interview flow`
- `docs: add safety boundaries`
- `test: add statement generation safety tests`
- `fix: preserve uncertainty in police statement draft`

## Safety Review

Before opening a pull request, check that the change:

- Does not fabricate facts
- Does not strengthen uncertain memories
- Does not give legal or medical advice
- Does not predict exact criminal penalties
- Does not encourage suspect confrontation
- Keeps user review before external sharing

## Pull Request Checklist

- [ ] Tests added or updated
- [ ] Safety boundary considered
- [ ] Privacy impact considered
- [ ] README or docs updated if behavior changed
- [ ] No API keys or real personal data included
