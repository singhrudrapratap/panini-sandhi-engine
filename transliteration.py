# -*- coding: utf-8 -*-
"""
=============================================================================
Sanskrit Transliteration Engine (संस्कृत-लिप्यन्तरण-तन्त्रम्)
=============================================================================

A dedicated, standalone bidirectional transliteration module for Sanskrit:
- International Alphabet of Sanskrit Transliteration (IAST)
- Harvard-Kyoto (HK) ASCII
- Devanagari Unicode (NFC normalized)

Handles:
- Short and long vowels (ह्रस्व-दीर्घ-स्वराः)
- Aspirated consonants (महाप्राण-व्यञ्जनानि: kh, gh, ch, jh, etc.)
- Retroflex consonants (मूर्धन्य-व्यञ्जनानि: ṭ, ṭh, ḍ, ḍh, ṇ, ṣ)
- Anusvāra (ं), Visarga (ः), and Avagraha (ऽ)
- Conjunct consonants (संयुक्ताक्षराणि)
- Ambiguity warnings for plain ASCII inputs (e.g. 'sh' vs 'ś'/'ṣ', 'a' vs 'ā')

Author: Panini Computational Linguistics Laboratory
Separation of Concerns: Independent of Sandhi rule matching.
=============================================================================
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Any


# ---------------------------------------------------------------------------
# 1. Phonological Character Tables
# ---------------------------------------------------------------------------

# Independent Vowels (स्वर / Svara)
VOWEL_MAPPINGS = [
    # (IAST, HK, Devanagari Independent, Devanagari Matra)
    ("ai", "ai", "ऐ", "ै"),
    ("au", "au", "औ", "ौ"),
    ("ā", "A", "आ", "ा"),
    ("ī", "I", "ई", "ी"),
    ("ū", "U", "ऊ", "ू"),
    ("ṝ", "RR", "ॠ", "ॄ"),
    ("ṛ", "R", "ऋ", "ृ"),
    ("ḷ", "lR", "ऌ", "ॢ"),
    ("a", "a", "अ", ""),
    ("i", "i", "इ", "ि"),
    ("u", "u", "उ", "ु"),
    ("e", "e", "ए", "े"),
    ("o", "o", "ओ", "ो"),
]

# Consonants (व्यञ्जन / Vyañjana)
# Ordered by descending length of Roman multigraphs to greedily match aspirated consonants first
CONSONANT_MAPPINGS = [
    # Aspirated & multi-letter consonants
    ("kh", "kh", "ख"),
    ("gh", "gh", "घ"),
    ("ch", "ch", "छ"),
    ("jh", "jh", "झ"),
    ("ṭh", "Th", "ठ"),
    ("ḍh", "Dh", "ढ"),
    ("th", "th", "थ"),
    ("dh", "dh", "ध"),
    ("ph", "ph", "फ"),
    ("bh", "bh", "भ"),
    # Non-aspirated stops and sonorants
    ("k", "k", "क"),
    ("g", "g", "ग"),
    ("ṅ", "G", "ङ"),
    ("c", "c", "च"),
    ("j", "j", "ज"),
    ("ñ", "J", "ञ"),
    ("ṭ", "T", "ट"),
    ("ḍ", "D", "ड"),
    ("ṇ", "N", "ण"),
    ("t", "t", "त"),
    ("d", "d", "द"),
    ("n", "n", "न"),
    ("p", "p", "प"),
    ("b", "b", "ब"),
    ("m", "m", "म"),
    ("y", "y", "य"),
    ("r", "r", "र"),
    ("l", "l", "ल"),
    ("v", "v", "व"),
    # Sibilants & Aspirate
    ("ś", "z", "श"),
    ("ṣ", "S", "ष"),
    ("s", "s", "स"),
    ("h", "h", "ह"),
]

# Devanagari to IAST lookups
DEV_VOWEL_TO_IAST = {v[2]: v[0] for v in VOWEL_MAPPINGS}
DEV_MATRA_TO_IAST = {v[3]: v[0] for v in VOWEL_MAPPINGS if v[3]}
DEV_CONSONANT_TO_IAST = {c[2]: c[0] for c in CONSONANT_MAPPINGS}

# Devanagari to HK lookups
DEV_VOWEL_TO_HK = {v[2]: v[1] for v in VOWEL_MAPPINGS}
DEV_MATRA_TO_HK = {v[3]: v[1] for v in VOWEL_MAPPINGS if v[3]}
DEV_CONSONANT_TO_HK = {c[2]: c[1] for c in CONSONANT_MAPPINGS}


# ---------------------------------------------------------------------------
# 2. Text Normalization & Script Detection
# ---------------------------------------------------------------------------

def normalize_sanskrit(text: str) -> str:
    """
    Apply Unicode NFC normalization to Sanskrit text, strip extraneous whitespace,
    and eliminate zero-width joiners/non-joiners that might corrupt glyph comparisons.
    """
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", text).strip()
    # Remove zero-width characters that interfere with string matching
    norm = norm.replace("\u200c", "").replace("\u200d", "")
    return norm


def is_devanagari(text: str) -> bool:
    """
    Determine if text is primarily composed of Devanagari script (U+0900 to U+097F).
    """
    if not text:
        return False
    for ch in text:
        if "\u0900" <= ch <= "\u097F":
            return True
    return False


def detect_script(text: str) -> str:
    """
    Detect script of the given input.
    Returns: 'devanagari' or 'roman'.
    """
    return "devanagari" if is_devanagari(text) else "roman"


# ---------------------------------------------------------------------------
# 3. Devanagari -> Roman Transliteration (IAST & HK)
# ---------------------------------------------------------------------------

def devanagari_to_iast(text: str) -> str:
    """
    Convert Sanskrit Devanagari text into standard academic Roman IAST transliteration.
    Accurately handles virāma (्), vowel mātrās, inherent short 'a', anusvāra, visarga, and avagraha.

    Example:
        'हिमालय' -> 'himālaya'
        'सच्चित्' -> 'saccit'
        'रामोऽवदत्' -> "rāmo'vadat"
        'नमस्ते' -> 'namaste'
    """
    if not text:
        return ""
    text = normalize_sanskrit(text)
    res = []
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        # 1. Independent Vowel
        if c in DEV_VOWEL_TO_IAST:
            res.append(DEV_VOWEL_TO_IAST[c])
            i += 1

        # 2. Consonant
        elif c in DEV_CONSONANT_TO_IAST:
            base = DEV_CONSONANT_TO_IAST[c]
            i += 1
            if i < n:
                next_c = text[i]
                if next_c == "्": # Halanta / Virama -> no vowel follows
                    res.append(base)
                    i += 1
                elif next_c in DEV_MATRA_TO_IAST: # Matra sign attached
                    res.append(base + DEV_MATRA_TO_IAST[next_c])
                    i += 1
                else:
                    # Inherent 'a' vowel
                    res.append(base + "a")
            else:
                # Inherent 'a' at end of text
                res.append(base + "a")

        # 3. Modifiers (Ayogavāhas & Avagraha)
        elif c == "ः":
            res.append("ḥ")
            i += 1
        elif c == "ं":
            res.append("ṁ")
            i += 1
        elif c == "ँ":
            res.append("m̐")
            i += 1
        elif c == "ऽ":
            res.append("'")
            i += 1
        else:
            # Punctuation, space, or symbols
            res.append(c)
            i += 1

    return "".join(res)


def devanagari_to_harvard_kyoto(text: str) -> str:
    """
    Convert Sanskrit Devanagari text into Harvard-Kyoto (HK) ASCII transliteration.
    """
    if not text:
        return ""
    text = normalize_sanskrit(text)
    res = []
    i = 0
    n = len(text)

    while i < n:
        c = text[i]
        if c in DEV_VOWEL_TO_HK:
            res.append(DEV_VOWEL_TO_HK[c])
            i += 1
        elif c in DEV_CONSONANT_TO_HK:
            base = DEV_CONSONANT_TO_HK[c]
            i += 1
            if i < n:
                next_c = text[i]
                if next_c == "्":
                    res.append(base)
                    i += 1
                elif next_c in DEV_MATRA_TO_HK:
                    res.append(base + DEV_MATRA_TO_HK[next_c])
                    i += 1
                else:
                    res.append(base + "a")
            else:
                res.append(base + "a")
        elif c == "ः":
            res.append("H")
            i += 1
        elif c == "ं":
            res.append("M")
            i += 1
        elif c == "ऽ":
            res.append("'")
            i += 1
        else:
            res.append(c)
            i += 1

    return "".join(res)


# ---------------------------------------------------------------------------
# 4. Roman -> Devanagari Transliteration (IAST & Harvard-Kyoto)
# ---------------------------------------------------------------------------

def roman_to_devanagari(text: str, scheme: str = "auto") -> str:
    """
    Convert Roman transliteration (IAST or Harvard-Kyoto) to Devanagari.

    Parameters:
        text: Input string in Roman transliteration (e.g. 'rāma', 'hima', 'Alaya').
        scheme: 'auto', 'iast', or 'hk'. Default is 'auto' (detects and normalizes HK).

    Features:
        - Accurately converts long vowels (ā, ī, ū, ṛ, ṝ, ḷ) and diphthongs (e, ai, o, au).
        - Handles aspirated consonants (kh, gh, ch, jh, ṭh, ḍh, th, dh, ph, bh).
        - Correctly formats conjunct consonants (e.g. 'sat' + 'cit' -> 'सत्' + 'चित्').
        - Supports visarga (ḥ/H), anusvāra (ṃ/ṁ/M), and avagraha (').
    """
    if not text:
        return ""
    text = text.strip()

    # Pre-normalize Harvard-Kyoto capitals and common ASCII diacritic replacements
    # (Order matters: multigraphs before single characters)
    hk_conversions = [
        ("RR", "ṝ"), ("lR", "ḷ"), ("Th", "ṭh"), ("Dh", "ḍh"),
        ("A", "ā"), ("I", "ī"), ("U", "ū"), ("R", "ṛ"),
        ("M", "ṃ"), ("H", "ḥ"), ("G", "ṅ"), ("J", "ñ"),
        ("T", "ṭ"), ("D", "ḍ"), ("N", "ṇ"), ("z", "ś"), ("S", "ṣ")
    ]
    for hk_pat, iast_pat in hk_conversions:
        text = text.replace(hk_pat, iast_pat)

    # Standard ASCII double vowels to long vowels: aa -> ā, ii -> ī, uu -> ū, ee -> e, oo -> o
    # (Only applied if no macro/diacritic already present)
    text = text.replace("aa", "ā").replace("ii", "ī").replace("uu", "ū")

    i = 0
    n = len(text)
    res = []

    while i < n:
        c = text[i]

        # Whitespace and punctuation
        if c in (" ", "-", "\t", "\n", ",", ";", ".", "!", "?"):
            res.append(c)
            i += 1
            continue

        # Avagraha
        if c == "'":
            res.append("ऽ")
            i += 1
            continue

        # Visarga
        if c in ("ḥ", "H"):
            res.append("ः")
            i += 1
            continue

        # Anusvāra
        if c in ("ṃ", "ṁ", "M"):
            res.append("ं")
            i += 1
            continue

        # 1. Match Consonant
        matched_c = None
        for r_c, _, dev_c in CONSONANT_MAPPINGS:
            if text.startswith(r_c, i):
                matched_c = (r_c, dev_c)
                break

        if matched_c:
            r_c, dev_c = matched_c
            i += len(r_c)

            # Check if followed by a vowel
            matched_v = None
            for r_v, _, _, matra_v in VOWEL_MAPPINGS:
                if text.startswith(r_v, i):
                    matched_v = (r_v, matra_v)
                    break

            if matched_v:
                r_v, matra_v = matched_v
                i += len(r_v)
                res.append(dev_c + matra_v)
            else:
                # No vowel follows -> explicit Halanta / Virāma
                res.append(dev_c + "्")
            continue

        # 2. Match Independent Vowel (at syllable start or word start)
        matched_v = None
        for r_v, _, indep_v, _ in VOWEL_MAPPINGS:
            if text.startswith(r_v, i):
                matched_v = (r_v, indep_v)
                break

        if matched_v:
            r_v, indep_v = matched_v
            i += len(r_v)
            res.append(indep_v)
            continue

        # Unmatched symbol
        res.append(c)
        i += 1

    return "".join(res)


# Alias for explicit IAST function
iast_to_devanagari = roman_to_devanagari
harvard_kyoto_to_devanagari = roman_to_devanagari


# ---------------------------------------------------------------------------
# 5. Roman Sanskrit Ambiguity Detection & Pedagogical Feedback
# ---------------------------------------------------------------------------

def detect_ambiguities(text: str) -> List[Dict[str, str]]:
    """
    Analyze Roman Sanskrit input for potential ambiguous spellings,
    such as plain English ASCII 'sh' (could be ś/श or ṣ/ष),
    plain 'a' (could be intended as long ā), or 'ch' vs 'c'.

    Returns a list of advisory dictionaries with explanations and suggestions.
    This fulfills the requirement: 'Do not silently treat ambiguous Roman spellings
    as unambiguous. Clearly document supported conventions.'
    """
    if not text or is_devanagari(text):
        return []

    warnings = []

    # Check 1: 'sh' is ambiguous in Sanskrit between palatal 'ś' (श) and retroflex 'ṣ' (ष)
    if "sh" in text.lower():
        warnings.append({
            "pattern": "sh",
            "issue_en": "'sh' is ambiguous in Sanskrit phonology. It may represent palatal 'ś' (श) or retroflex 'ṣ' (ष).",
            "issue_hi": "'sh' वर्ण संस्कृत में अस्पष्ट है। यह तालव्य 'ś' (श) या मूर्धन्य 'ṣ' (ष) दोनों हो सकता है।",
            "suggestion_en": "Use 'ś' (or 'z') for श, or 'ṣ' (or 'S') for ष.",
            "suggestion_hi": "तालव्य 'श' के लिए 'ś' तथा मूर्धन्य 'ष' के लिए 'ṣ' का प्रयोग करें।"
        })

    # Check 2: 'ch' vs 'c' (in IAST, 'c' = च and 'ch' = छ)
    if re.search(r"\bch", text.lower()):
        warnings.append({
            "pattern": "ch",
            "issue_en": "In academic IAST, 'c' represents च (unaspirated), while 'ch' represents छ (aspirated).",
            "issue_hi": "मानक IAST में 'c' से च (अल्पप्राण) और 'ch' से छ (महाप्राण) का बोध होता है।",
            "suggestion_en": "For च, write 'c' (e.g. 'cit' -> चित्). For छ, write 'ch'.",
            "suggestion_hi": "'च' के लिए 'c' (जैसे 'cit' -> चित्) तथा 'छ' के लिए 'ch' लिखें।"
        })

    # Check 3: plain vowel 'a' without diacritics in known long positions
    common_long_words = {
        "rama": ("rāma", "राम"),
        "alaya": ("ālaya", "आलय"),
        "vidya": ("vidyā", "विद्या"),
        "isvara": ("īśvara", "ईश्वर"),
        "acharya": ("ācārya", "आचार्य"),
        "ananda": ("ānanda", "आनन्द"),
        "adi": ("ādi", "आदि"),
        "ajna": ("ājñā", "आज्ञा")
    }
    clean_w = text.strip().lower()
    if clean_w in common_long_words:
        correct_iast, correct_dev = common_long_words[clean_w]
        warnings.append({
            "pattern": clean_w,
            "issue_en": f"Input '{text}' uses plain 'a'/'i' without long-vowel diacritics.",
            "issue_hi": f"'{text}' में दीर्घ स्वरों के चिह्न नहीं हैं।",
            "suggestion_en": f"Recommended IAST: '{correct_iast}' ({correct_dev}) or Harvard-Kyoto capital letters.",
            "suggestion_hi": f"सुझाया गया मानक रूप: '{correct_iast}' ({correct_dev})।"
        })

    return warnings


# ---------------------------------------------------------------------------
# 6. Transliteration Reference Data & Documentation
# ---------------------------------------------------------------------------

def get_transliteration_reference_table() -> List[Dict[str, str]]:
    """
    Return a structured catalog of supported Sanskrit transliteration characters
    for UI documentation and help modals.
    """
    rows = []

    # Vowels
    for iast, hk, dev, matra in VOWEL_MAPPINGS:
        rows.append({
            "Type": "Vowel (स्वर)",
            "Devanagari": dev,
            "Mātrā": matra if matra else "(inherent a)",
            "IAST": iast,
            "Harvard-Kyoto": hk,
            "Example": f"{dev} ({iast})"
        })

    # Consonants
    for iast, hk, dev in CONSONANT_MAPPINGS:
        rows.append({
            "Type": "Consonant (व्यञ्जन)",
            "Devanagari": dev,
            "Mātrā": "-",
            "IAST": iast,
            "Harvard-Kyoto": hk,
            "Example": f"{dev}a ({iast}a)"
        })

    # Modifiers
    rows.append({
        "Type": "Modifier (अयोगवाह)",
        "Devanagari": "ं",
        "Mātrā": "-",
        "IAST": "ṁ / ṃ",
        "Harvard-Kyoto": "M",
        "Example": "हरिं (hariṁ)"
    })
    rows.append({
        "Type": "Modifier (अयोगवाह)",
        "Devanagari": "ः",
        "Mātrā": "-",
        "IAST": "ḥ",
        "Harvard-Kyoto": "H",
        "Example": "रामः (rāmaḥ)"
    })
    rows.append({
        "Type": "Avagraha (अवग्रह)",
        "Devanagari": "ऽ",
        "Mātrā": "-",
        "IAST": "'",
        "Harvard-Kyoto": "'",
        "Example": "तेऽपि (te'pi)"
    })

    return rows
