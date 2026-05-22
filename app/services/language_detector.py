from langdetect import detect, DetectorFactory

# Makes results consistent
DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ga": "Irish (Gaeilge)",
    "pl": "Polish", 
    "ro": "Romanian",
    "pt": "Portuguese",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ar": "Arabic",
    "hi": "Hindi",
    "ur": "Urdu",
    "zh-cn": "Chinese",
    "fil": "Filipino",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "uk": "Ukrainian",
    "ru": "Russian"
}

def detect_language(text: str) -> str:
    """Detect language of text, return language code."""
    try:
        lang = detect(text[:1000])
        return lang if lang in SUPPORTED_LANGUAGES else "en"
    except:
        return "en"

def get_language_name(code: str) -> str:
    """Get human readable language name."""
    return SUPPORTED_LANGUAGES.get(code, "English")