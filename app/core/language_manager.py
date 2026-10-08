import json
from pathlib import Path
from app.config import SETTINGS_FILE, DEFAULT_SETTINGS


class LanguageManager:
    def __init__(self):
        self.locales_dir = Path(__file__).parent.parent / "locales"
        self.current_lang = "en"
        self.translations = {}
        self.settings = self._load_settings()
        self.current_lang = self.settings.get("language", "en")
        self.load_translations(self.current_lang)

    def _load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def _save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_available_languages(self):
        result = []
        for path in sorted(self.locales_dir.glob("*.json")):
            code = path.stem
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("_language_name", code)
                result.append((code, name))
            except Exception:
                continue
        return result

    def load_translations(self, lang_code):
        path = self.locales_dir / f"{lang_code}.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
                    self.current_lang = lang_code
                    return True
            except Exception:
                pass
        if lang_code != "en":
            return self.load_translations("en")
        return False

    def save_language_preference(self, lang_code):
        self.settings["language"] = lang_code
        self._save_settings()

    def get(self, key, default=None, **kwargs):
        text = self.translations.get(key, default or key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text