# Security Policy

## Supported Versions

This repository is an early MVP. Security fixes should target the latest `main` branch.

## Sensitive Data

Do not commit:

- `.env` files
- API keys
- Real case records
- Personal identity documents
- Police event numbers from real users
- Medical records
- Screenshots containing private user details

## API Keys

The app supports local API-key configuration. Keys should stay in local environment variables or browser-local settings. They should never be hard-coded into source files, examples, tests, docs, or screenshots.

## Responsible Disclosure

If you discover a vulnerability, please open a private report with reproduction steps, affected files, and suggested mitigation. Do not post real personal data in public issues.

## Safety-Critical Reports

For issues involving unsafe advice, legal hallucinations, medical claims, or pressure toward confrontation, include the prompt, generated output, and expected safer behavior.
