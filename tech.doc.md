# Vaani Smart Data Intelligence — Technical Document

## Architecture Overview
Vaani is a deterministic data assistant that uses a rule-based engine to translate natural language into SQL.

### Core Components
1. **Rule Engine (`ai/rule_engine.py`)**: A programmatic parser that uses regex and schema awareness to generate SQL.
2. **Summary Builder (`voice/summary_builder.py`)**: A deterministic generator that creates human-readable summaries from data results.
3. **Voice Layer (`voice/sarvam_stt.py` & `sarvam_tts.py`)**: Integration with Sarvam AI for multilingual voice support.
4. **Validation (`validators/sql_validator.py`)**: A 6-step security check for all generated SQL.

## Data Flow
`User Query` -> `Rule Engine` -> `SQL Validator` -> `Database` -> `Summary Builder` -> `Sarvam TTS`
