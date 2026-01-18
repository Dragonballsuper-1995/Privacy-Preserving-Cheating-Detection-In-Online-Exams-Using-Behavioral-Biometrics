# Internationalization Support

**i18n Configuration for Multi-Language Support**

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Mandarin (zh)

## Translation Files

Create JSON files in `backend/app/i18n/`:

- `en.json` - English (default)
- `es.json` - Spanish
- `fr.json` - French
- `de.json` - German
- `zh.json` - Mandarin

## Example Structure (en.json)

```json
{
  "risk_levels": {
    "low": "Low Risk",
    "medium": "Medium Risk",
    "high": "High Risk",
    "critical": "Critical Risk"
  },
  "messages": {
    "flagged": "This session has been flagged for review",
    "analysis_complete": "Analysis completed successfully"
  },
  "risk_factors": {
    "paste_detected": "Content pasted: {count} paste events",
    "tab_switching": "Tab switching detected: {count} times",
    "extended_pause": "Extended pause: {duration}s"
  },
  "errors": {
    "session_not_found": "Session not found",
    "unauthorized": "Unauthorized access"
  }
}
```

## Usage

```python
from app.i18n import get_translation

# Get translated text
t = get_translation(lang="es")
message = t("messages.flagged")  # "Esta sesión ha sido marcada para revisión"
```

## Implementation Note

Full i18n implementation requires:
1. Translation files for all supported languages
2. i18n middleware for automatic language detection
3. API parameter for language selection
4. Frontend localization integration

**Status:** Framework ready, translations to be added as needed.
