# Technical Specification — Vaani

## 1. System Goals
To provide a deterministic, fast, and secure interface for banking data using natural language and voice.

## 2. SQL Pipeline
The system uses a **Rule-Based Analyzer** that maps user intent to SQL templates. All SQL is validated against a whitelist of commands and the `user_uploaded_data` table.

## 3. Voice Interface
Leverages **Sarvam AI** for:
- Speech-to-Text: `saarika:v2`
- Text-to-Speech: `bulbul:v1`

## 4. Security
- No LLM execution of code.
- Read-only database access for queries.
- SQL keyword blacklisting.
