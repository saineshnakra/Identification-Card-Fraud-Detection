# Security and privacy

## Scope

`id-tamper-check` is an educational image-comparison tool, not an identity-verification service. It runs entirely
locally on the files you pass to it and never uploads images anywhere. (The optional web demo processes images on
whatever server hosts it; see below.)

## Handling documents

- Do not commit real identity documents, personal data, API keys, or images you are not authorized to use.
  Use the synthetic generator (`id_tamper_check.samples`) or explicitly licensed specimens.
- Do not upload real identity documents to a public deployment of the web demo, such as a Hugging Face Space.

## Reporting a vulnerability

Please report security issues privately using
[GitHub private vulnerability reporting](https://github.com/saineshnakra/Identification-Card-Fraud-Detection/security/advisories/new),
or through the contact details at [sainesh.com](https://sainesh.com/). Do not open a public issue, and never include
sensitive documents or personal information in a report.

Only the latest release receives fixes.
