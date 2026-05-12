# Privacy Policy

SafeAbroad Agent is designed as a privacy-first assistant for sensitive incident documentation.

## Data Minimisation

The app should only collect information necessary for incident documentation and user support. Users should avoid entering unrelated private information.

## Local-First Design

Where possible, sensitive information should be stored locally on the user's device. Local `.env` files, API keys, test caches, and private case data must not be committed to Git.

## User Control

Users should be able to:

- Review generated text before sharing it
- Edit timelines and statements
- Mark memories as uncertain
- Export their own records
- Delete local case data

## Sensitive Data Warning

Users should avoid entering unnecessary:

- Passport numbers
- Bank details
- Immigration records
- Medical record numbers
- Full addresses unrelated to the incident
- Third-party private information not needed for documentation

## LLM Provider Warning

If a cloud LLM provider is configured, incident text may be sent to that provider for processing. Users should review the provider's privacy terms and avoid sending unnecessary sensitive data. Deterministic fallback logic is available when no provider is configured.

## Redaction

Generated exports should support redaction of names, phone numbers, emails, addresses, and other identifiers when the user wants a safer sharing copy.
