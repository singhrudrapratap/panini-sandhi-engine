# -*- coding: utf-8 -*-
"""
=============================================================================
Pāṇini Vyākaraṇa Sandhi Rule Engine (पाणिनीय-व्याकरण-सन्धिनियम-तन्त्रम्)
=============================================================================

A modular, rule-based computational engine for Sanskrit Sandhi analysis,
grounded in the classical sutras of Pāṇini's Aṣṭādhyāyī and Bhaṭṭoji Dīkṣita's
Siddhānta Kaumudī.

Designed for Sanskrit grammar researchers, students, and computational
linguistics demonstrations.

Author: Panini Computational Linguistics Laboratory
Architecture: Pure Python, Rule-Based, Transparent, Fully Documented
=============================================================================
"""

import json
import os
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


# ---------------------------------------------------------------------------
# 1. Phonological Constants & Inventories (वर्णमाला)
# ---------------------------------------------------------------------------

# Primary Sanskrit Vowels (अच् / Svaras)
VOWELS_INDEPENDENT = ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ॠ", "ऌ", "ए", "ऐ", "ओ", "औ"]

# Dependent Vowel Signs (मात्रा / Mātrās)
MATRAS = ["ा", "ि", "ी", "ु", "ू", "ृ", "ॄ", "ॢ", "े", "ै", "ो", "ौ"]

# Bidirectional Mātrā <-> Independent Vowel Mapping
MATRA_TO_VOWEL = {
    "ा": "आ", "ि": "इ", "ी": "ई", "ु": "उ", "ू": "ऊ",
    "ृ": "ऋ", "ॄ": "ॠ", "ॢ": "ऌ", "े": "ए", "ै": "ऐ",
    "ो": "ओ", "ौ": "औ"
}

VOWEL_TO_MATRA = {
    "अ": "", "आ": "ा", "इ": "ि", "ई": "ी", "उ": "ु", "ऊ": "ू",
    "ऋ": "ृ", "ॠ": "ॄ", "ऌ": "ॢ", "ए": "े", "ऐ": "ै", "ओ": "ो", "औ": "ौ"
}

# Consonant Inventory (हल् / Vyañjanas)
CONSONANTS = set("कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह")

# Consonant Class Groupings (वर्ग / Varga)
VARGA_KA = ["क", "ख", "ग", "घ", "ङ"]
VARGA_CA = ["च", "छ", "ज", "झ", "ञ"]
VARGA_TA_RETRO = ["ट", "ठ", "ड", "ढ", "ण"]
VARGA_TA_DENTAL = ["त", "थ", "द", "ध", "न"]
VARGA_PA = ["प", "फ", "ब", "भ", "म"]

# Voiced Consonants (हश् / Haś)
VOICED_CONSONANTS = set("गघङजझञडढणदधनबभमयरलवह")

# Voiceless Consonants (खर् / Khar)
VOICELESS_CONSONANTS = set("कखचछटठतथपफशषस")

# Nasals (अनुनासिक)
NASALS = set("ङञणनम")

# Dental to Palatal Mapping (Ścutva Sandhi: स्तोः श्चुना श्चुः 8.4.40)
DENTAL_TO_PALATAL = {
    "स्": "श्", "त्": "च्", "थ्": "छ्", "द्": "ज्", "ध्": "झ्", "न्": "ञ्"
}

# Dental to Retroflex Mapping (Ṣṭutva Sandhi: ष्टुना ष्टुः 8.4.41)
DENTAL_TO_RETROFLEX = {
    "स्": "ष्", "त्": "ट्", "थ्": "ठ्", "द्": "ड्", "ध्": "ढ्", "न्": "ण्"
}

# First letter to Third letter mapping (Jaśtva: झलां जशोऽन्ते 8.2.39)
STOP_TO_THIRD = {
    "क्": "ग्", "च्": "ज्", "ट्": "ड्", "त्": "द्", "प्": "ब्"
}

# Voiced stop to First letter mapping (Cartva: खरि च 8.4.55)
VOICED_TO_FIRST = {
    "ग्": "क्", "ज्": "च्", "ड्": "ट्", "द्": "त्", "ब्": "प्"
}

# Stop to Nasal mapping (Anunāsika: यरोऽनुनासिकेऽनुनासिको वा 8.4.45)
STOP_TO_NASAL = {
    "क्": "ङ्", "ट्": "ण्", "त्": "न्", "प्": "म्"
}

# Savarṇa (Homogeneous Vowel) Families (सवर्णाः)
SAVARNA_FAMILIES = {
    "अ": "A_FAMILY", "आ": "A_FAMILY",
    "इ": "I_FAMILY", "ई": "I_FAMILY",
    "उ": "U_FAMILY", "ऊ": "U_FAMILY",
    "ऋ": "R_FAMILY", "ॠ": "R_FAMILY", "ऌ": "R_FAMILY" # ऌ and ऋ are savarna by kārikā
}

LONG_EQUIVALENT = {
    "A_FAMILY": "आ",
    "I_FAMILY": "ई",
    "U_FAMILY": "ऊ",
    "R_FAMILY": "ॠ"
}


# ---------------------------------------------------------------------------
# 2. Data Transfer Object: SandhiResult
# ---------------------------------------------------------------------------

@dataclass
class SandhiResult:
    """
    Structured outcome of a Sandhi analysis.
    Contains both linguistic metadata, transliterated outputs, and bilingual explanations.
    """
    status: str                          # 'success', 'unsupported', 'error', 'no_sandhi'
    word1: str                           # Pūrva-pada in Devanagari
    word2: str                           # Uttara-pada in Devanagari
    combined: str                        # Sandhi result in Devanagari
    word1_iast: str = ""                 # Pūrva-pada in Roman IAST
    word2_iast: str = ""                 # Uttara-pada in Roman IAST
    combined_iast: str = ""              # Combined form in Roman IAST
    rule_id: str = ""                    # e.g. 'SVAR_01'
    rule_name: str = ""                  # Active rule name (localized)
    rule_name_en: str = ""               # English rule name
    rule_name_hi: str = ""               # Hindi rule name
    category: str = ""                   # Active category (localized)
    category_en: str = ""                # English category
    category_hi: str = ""                # Hindi category
    sutra: str = ""                      # Classical Pāṇini sūtra
    reference: str = ""                  # Aṣṭādhyāyī reference (e.g. 6.1.101)
    boundary_breakdown: str = ""         # Active step-by-step phoneme breakdown (localized)
    boundary_breakdown_en: str = ""      # English breakdown
    boundary_breakdown_hi: str = ""      # Hindi breakdown
    explanation: str = ""                # Active pedagogical explanation (localized)
    explanation_en: str = ""             # English explanation
    explanation_hi: str = ""             # Hindi explanation
    transformation_detail: str = ""      # Active transformation detail (localized)
    transformation_detail_en: str = ""   # English detail
    transformation_detail_hi: str = ""   # Hindi detail
    error_message: Optional[str] = None  # Reason for failure if status != 'success'
    error_message_en: Optional[str] = None
    error_message_hi: Optional[str] = None
    language: str = "en"                 # 'en' or 'hi'
    ambiguity_warnings: List[Dict[str, str]] = field(default_factory=list)

    def localized(self, lang: str = "en") -> "SandhiResult":
        """
        Return a localized view of this result in either English or Hindi.
        Sanskrit word forms (Devanagari & IAST) are strictly preserved.
        """
        is_hi = (lang == "hi")
        active_rule = self.rule_name_hi if (is_hi and self.rule_name_hi) else (self.rule_name_en or self.rule_name)
        active_cat = self.category_hi if (is_hi and self.category_hi) else (self.category_en or self.category)
        active_exp = self.explanation_hi if (is_hi and self.explanation_hi) else (self.explanation_en or self.explanation)
        active_bb = self.boundary_breakdown_hi if (is_hi and self.boundary_breakdown_hi) else (self.boundary_breakdown_en or self.boundary_breakdown)
        active_trans = self.transformation_detail_hi if (is_hi and self.transformation_detail_hi) else (self.transformation_detail_en or self.transformation_detail)
        active_err = self.error_message_hi if (is_hi and self.error_message_hi) else (self.error_message_en or self.error_message)

        return SandhiResult(
            status=self.status,
            word1=self.word1,
            word2=self.word2,
            combined=self.combined,
            word1_iast=self.word1_iast,
            word2_iast=self.word2_iast,
            combined_iast=self.combined_iast,
            rule_id=self.rule_id,
            rule_name=active_rule,
            rule_name_en=self.rule_name_en or self.rule_name,
            rule_name_hi=self.rule_name_hi or self.rule_name,
            category=active_cat,
            category_en=self.category_en or self.category,
            category_hi=self.category_hi or self.category,
            sutra=self.sutra,
            reference=self.reference,
            boundary_breakdown=active_bb,
            boundary_breakdown_en=self.boundary_breakdown_en or self.boundary_breakdown,
            boundary_breakdown_hi=self.boundary_breakdown_hi or self.boundary_breakdown,
            explanation=active_exp,
            explanation_en=self.explanation_en or self.explanation,
            explanation_hi=self.explanation_hi or self.explanation,
            transformation_detail=active_trans,
            transformation_detail_en=self.transformation_detail_en or self.transformation_detail,
            transformation_detail_hi=self.transformation_detail_hi or self.transformation_detail,
            error_message=active_err,
            error_message_en=self.error_message_en or self.error_message,
            error_message_hi=self.error_message_hi or self.error_message,
            language=lang,
            ambiguity_warnings=self.ambiguity_warnings
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a standard dictionary representation."""
        return {
            "status": self.status,
            "word1": self.word1,
            "word2": self.word2,
            "combined": self.combined,
            "word1_iast": self.word1_iast,
            "word2_iast": self.word2_iast,
            "combined_iast": self.combined_iast,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_name_en": self.rule_name_en,
            "rule_name_hi": self.rule_name_hi,
            "category": self.category,
            "category_en": self.category_en,
            "category_hi": self.category_hi,
            "sutra": self.sutra,
            "reference": self.reference,
            "boundary_breakdown": self.boundary_breakdown,
            "boundary_breakdown_en": self.boundary_breakdown_en,
            "boundary_breakdown_hi": self.boundary_breakdown_hi,
            "explanation": self.explanation,
            "explanation_en": self.explanation_en,
            "explanation_hi": self.explanation_hi,
            "transformation_detail": self.transformation_detail,
            "transformation_detail_en": self.transformation_detail_en,
            "transformation_detail_hi": self.transformation_detail_hi,
            "error_message": self.error_message,
            "error_message_en": self.error_message_en,
            "error_message_hi": self.error_message_hi,
            "language": self.language,
            "ambiguity_warnings": self.ambiguity_warnings
        }


# ---------------------------------------------------------------------------
# 3. Transliteration System (Devanagari <-> IAST / Harvard-Kyoto)
# ---------------------------------------------------------------------------

VOWELS_DEV_TO_IAST = {
    "अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū",
    "ऋ": "ṛ", "ॠ": "ṝ", "ऌ": "ḷ", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au"
}

MATRA_DEV_TO_IAST = {
    "ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū",
    "ृ": "ṛ", "ॄ": "ṝ", "ॢ": "ḷ", "े": "e", "ै": "ai", "ो": "o", "ौ": "au"
}

CONSONANTS_DEV_TO_IAST = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ṅ",
    "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "ñ",
    "ट": "ṭ", "ठ": "ṭh", "ड": "ḍ", "ढ": "ḍh", "ण": "ṇ",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "ś", "ष": "ṣ", "स": "s", "ह": "h"
}

# Roman consonants sorted descending by length to greedy-match multigraphs
ROMAN_CONSONANTS_TABLE = [
    ("kh", "ख"), ("gh", "घ"), ("ch", "छ"), ("jh", "झ"),
    ("ṭh", "ठ"), ("ḍh", "ढ"), ("th", "थ"), ("dh", "ध"),
    ("ph", "फ"), ("bh", "भ"),
    ("k", "क"), ("g", "ग"), ("ṅ", "ङ"),
    ("c", "च"), ("j", "ज"), ("ñ", "ञ"),
    ("ṭ", "ट"), ("ḍ", "ड"), ("ṇ", "ण"),
    ("t", "त"), ("d", "द"), ("n", "न"),
    ("p", "प"), ("b", "ब"), ("m", "म"),
    ("y", "य"), ("r", "र"), ("l", "ल"), ("v", "व"),
    ("ś", "श"), ("ṣ", "ष"), ("s", "स"), ("h", "ह")
]

ROMAN_VOWELS_TABLE = [
    ("ai", "ऐ", "ै"), ("au", "औ", "ौ"),
    ("ā", "आ", "ा"), ("ī", "ई", "ी"), ("ū", "ऊ", "ू"),
    ("ṛ", "ऋ", "ृ"), ("ṝ", "ॠ", "ॄ"), ("ḷ", "ऌ", "ॢ"),
    ("a", "अ", ""), ("i", "इ", "ि"), ("u", "उ", "ु"),
    ("e", "ए", "े"), ("o", "ओ", "ो")
]


def is_devanagari(text: str) -> bool:
    """
    Check if a string contains predominantly Devanagari Unicode characters.
    Devanagari Unicode block is U+0900 to U+097F.
    """
    for ch in text:
        if "\u0900" <= ch <= "\u097F":
            return True
    return False


def normalize_sanskrit(text: str) -> str:
    """
    Normalize Sanskrit text using Unicode NFC form,
    strip leading/trailing whitespaces, remove non-phonemic symbols,
    while preserving all essential Sanskrit diacritics.
    """
    if not text:
        return ""
    # Unicode Normalization (NFC merges combining characters cleanly)
    norm = unicodedata.normalize("NFC", text).strip()
    # Normalize varied representations of danda or internal artifacts
    norm = norm.replace("\u200c", "").replace("\u200d", "") # remove zero-width non-joiner / joiner
    return norm


def devanagari_to_iast(text: str) -> str:
    """
    Convert Sanskrit Devanagari text into standard academic Roman IAST transliteration.
    Correctly resolves virama, vowel signs, inherent 'a', anusvara, and visarga.
    """
    if not text:
        return ""
    text = normalize_sanskrit(text)
    res = []
    i = 0
    n = len(text)

    while i < n:
        c = text[i]
        if c in VOWELS_DEV_TO_IAST:
            res.append(VOWELS_DEV_TO_IAST[c])
            i += 1
        elif c in CONSONANTS_DEV_TO_IAST:
            base = CONSONANTS_DEV_TO_IAST[c]
            i += 1
            if i < n:
                next_c = text[i]
                if next_c == "्": # Virama (Halanta)
                    res.append(base)
                    i += 1
                elif next_c in MATRA_DEV_TO_IAST: # Matra attached
                    res.append(base + MATRA_DEV_TO_IAST[next_c])
                    i += 1
                else:
                    # Inherent vowel 'a'
                    res.append(base + "a")
            else:
                # Inherent vowel 'a' at end
                res.append(base + "a")
        elif c == "ः":
            res.append("ḥ")
            i += 1
        elif c == "ं":
            res.append("ṁ")
            i += 1
        elif c == "ऽ":
            res.append("'")
            i += 1
        else:
            res.append(c)
            i += 1

    return "".join(res)


def roman_to_devanagari(text: str) -> str:
    """
    Convert Roman transliteration (IAST or Harvard-Kyoto) to Devanagari.
    Enables beginners to type 'hima' or 'Alaya' and receive proper Devanagari.
    """
    if not text:
        return ""
    text = text.strip()

    # Pre-normalize common Harvard-Kyoto replacements
    hk_replacements = [
        ("RR", "ṝ"), ("lR", "ḷ"), ("Th", "ṭh"), ("Dh", "ḍh"),
        ("A", "ā"), ("I", "ī"), ("U", "ū"), ("R", "ṛ"),
        ("M", "ṃ"), ("H", "ḥ"), ("G", "ṅ"), ("J", "ñ"),
        ("T", "ṭ"), ("D", "ḍ"), ("N", "ṇ"), ("z", "ś"), ("S", "ṣ")
    ]
    for hk_src, iast_target in hk_replacements:
        text = text.replace(hk_src, iast_target)

    # Convert common ASCII approximations (e.g. aa -> ā, ii -> ī, uu -> ū)
    text = text.replace("aa", "ā").replace("ii", "ī").replace("uu", "ū")

    i = 0
    n = len(text)
    res = []

    while i < n:
        c = text[i]
        if c in (" ", "-", "\t", "\n"):
            res.append(c)
            i += 1
            continue
        if c == "'":
            res.append("ऽ")
            i += 1
            continue
        if c in ("ḥ", "H"):
            res.append("ः")
            i += 1
            continue
        if c in ("ṃ", "ṁ", "M"):
            res.append("ं")
            i += 1
            continue

        # 1. Match consonant
        matched_c = None
        for r_c, dev_c in ROMAN_CONSONANTS_TABLE:
            if text.startswith(r_c, i):
                matched_c = (r_c, dev_c)
                break

        if matched_c:
            r_c, dev_c = matched_c
            i += len(r_c)

            # Check if followed by vowel
            matched_v = None
            for r_v, _, matra_v in ROMAN_VOWELS_TABLE:
                if text.startswith(r_v, i):
                    matched_v = (r_v, matra_v)
                    break

            if matched_v:
                r_v, matra_v = matched_v
                i += len(r_v)
                res.append(dev_c + matra_v)
            else:
                # No vowel follows -> Halanta consonant
                res.append(dev_c + "्")
            continue

        # 2. Match independent vowel at syllable/word beginning
        matched_v = None
        for r_v, indep_v, _ in ROMAN_VOWELS_TABLE:
            if text.startswith(r_v, i):
                matched_v = (r_v, indep_v)
                break

        if matched_v:
            r_v, indep_v = matched_v
            i += len(r_v)
            res.append(indep_v)
            continue

        # Non-alphabetical symbol
        res.append(c)
        i += 1

    return "".join(res)


# ---------------------------------------------------------------------------
# 4. Phoneme Boundary Analysis (वर्ण-विच्छेद / Varṇa-Viccheda)
# ---------------------------------------------------------------------------

def join_stem_with_vowel(stem_halanta: str, vowel: str) -> str:
    """
    Combine a halanta consonant stem (e.g. 'हिम्', 'विद्य्') with a vowel.
    If stem ends in '्', removes '्' and applies the vowel's mātrā.
    If stem is empty, returns the independent vowel directly.
    """
    if not stem_halanta:
        return vowel
    if stem_halanta.endswith("्"):
        base = stem_halanta[:-1]
        matra = VOWEL_TO_MATRA.get(vowel, "")
        return base + matra
    return stem_halanta + vowel


def decompose_purva_pada(word: str) -> Tuple[str, str, str, Optional[str]]:
    """
    Analyze the final phonological boundary of the first word (Pūrva-pada).

    Returns:
        (stem, ending_type, ending_phoneme, pre_visarga_vowel)
        - stem: base word without final vowel/halanta marker
        - ending_type: 'vowel', 'halanta', 'visarga'
        - ending_phoneme: e.g. 'अ', 'आ', 'इ', 'त्', 'क्', 'ः'
        - pre_visarga_vowel: vowel before visarga (if ending_type is 'visarga')
    """
    word = normalize_sanskrit(word)
    if not word:
        return "", "", "", None

    # Case A: Word ends with Visarga (ः)
    if word.endswith("ः"):
        stem_before_vis = word[:-1]
        if not stem_before_vis:
            return "", "visarga", "ः", "अ"

        last_char = stem_before_vis[-1]
        if last_char in MATRA_TO_VOWEL:
            vowel = MATRA_TO_VOWEL[last_char]
            base_stem = stem_before_vis[:-1] + "्"
            return base_stem, "visarga", "ः", vowel
        elif last_char in CONSONANTS:
            # Consonant with inherent 'a'
            base_stem = stem_before_vis + "्"
            return base_stem, "visarga", "ः", "अ"
        elif last_char in VOWELS_INDEPENDENT:
            return "", "visarga", "ः", last_char
        else:
            return stem_before_vis, "visarga", "ः", "अ"

    # Case B: Word ends with explicit Halanta (्)
    if word.endswith("्"):
        if len(word) >= 2 and word[-2] in CONSONANTS:
            c = word[-2] + "्"
            stem = word[:-2]
            return stem, "halanta", c, None
        return word[:-1], "halanta", word, None

    # Case C: Word ends with a dependent vowel sign (Mātrā)
    if word[-1] in MATRA_TO_VOWEL:
        vowel = MATRA_TO_VOWEL[word[-1]]
        stem = word[:-1] + "्"
        return stem, "vowel", vowel, None

    # Case D: Word is an isolated independent vowel
    if word in VOWELS_INDEPENDENT:
        return "", "vowel", word, None

    # Case E: Word ends with a consonant having an implicit inherent 'a' (अ)
    if word[-1] in CONSONANTS:
        stem = word + "्"
        return stem, "vowel", "अ", None

    return word[:-1], "other", word[-1], None


def decompose_uttara_pada(word: str) -> Tuple[str, bool, str]:
    """
    Analyze the initial phonological boundary of the second word (Uttara-pada).

    Returns:
        (initial_phoneme, is_vowel, remainder)
        - initial_phoneme: e.g. 'आ', 'ई', 'च', 'त', 'ग'
        - is_vowel: True if initial_phoneme is a vowel
        - remainder: rest of the word following the initial sound
    """
    word = normalize_sanskrit(word)
    if not word:
        return "", False, ""

    first_char = word[0]

    # Case A: Begins with an independent vowel
    if first_char in VOWELS_INDEPENDENT:
        return first_char, True, word[1:]

    # Case B: Begins with a consonant
    if first_char in CONSONANTS:
        return first_char, False, word[1:]

    return first_char, False, word[1:]


# ---------------------------------------------------------------------------
# 5. The Panini Sandhi Engine Class
# ---------------------------------------------------------------------------

class PaniniSandhiEngine:
    """
    Core Rule Engine implementing verified Sanskrit Sandhi transformations
    from Pāṇini's Aṣṭādhyāyī.

    Separates phonological matching, morphological joining, and rule metadata.
    """

    def __init__(self, rules_file_path: Optional[str] = None):
        """
        Initialize the Sandhi Engine. Loads verified rules from rules.json.
        """
        if rules_file_path is None:
            # Default to rules.json in the same directory as this module
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            rules_file_path = os.path.join(curr_dir, "rules.json")

        self.rules_file_path = rules_file_path
        self.rules_data: Dict[str, Any] = {}
        self.rules_list: List[Dict[str, Any]] = []
        self.rules_by_id: Dict[str, Dict[str, Any]] = {}
        self.load_rules(rules_file_path)

    def load_rules(self, rules_path: str) -> None:
        """Load and index rule definitions from JSON file."""
        if not os.path.exists(rules_path):
            raise FileNotFoundError(
                f"Sanskrit Sandhi rules file not found at: '{rules_path}'. "
                "Ensure rules.json exists."
            )

        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules_data = json.load(f)

        self.rules_list = self.rules_data.get("rules", [])
        self.rules_by_id = {r["rule_id"]: r for r in self.rules_list}

    def get_categories(self) -> List[str]:
        """Return list of supported Sandhi categories."""
        return self.rules_data.get(
            "categories",
            [
                "Svara Sandhi (स्वरसन्धिः)",
                "Vyañjana Sandhi (व्यञ्जनसन्धिः)",
                "Visarga Sandhi (विसर्गसन्धिः)"
            ]
        )

    def get_rules_by_category(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter rules by category name, or return all if None or 'All'."""
        if not category or category == "All" or "All" in category:
            return self.rules_list
        return [r for r in self.rules_list if category.lower() in r["category"].lower()]

    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve rule definition by its unique identifier."""
        return self.rules_by_id.get(rule_id)

    def get_all_examples(self) -> List[Dict[str, Any]]:
        """Return a flat list of all worked classical examples from rules.json."""
        all_examples = []
        for r in self.rules_list:
            for ex in r.get("examples", []):
                ex_copy = dict(ex)
                ex_copy["rule_id"] = r["rule_id"]
                ex_copy["rule_name"] = r["rule_name"]
                ex_copy["category"] = r["category"]
                all_examples.append(ex_copy)
        return all_examples

    # -----------------------------------------------------------------------
    # 6. Main Analysis Method
    # -----------------------------------------------------------------------

    def analyze(
        self,
        word1_input: str,
        word2_input: str,
        category_filter: Optional[str] = None,
        language: str = "en"
    ) -> SandhiResult:
        """
        Analyze the Sandhi between two Sanskrit words or morpheme parts.

        Parameters:
            word1_input: Preceding word (Pūrva-pada), in Devanagari or Roman IAST.
            word2_input: Succeeding word (Uttara-pada), in Devanagari or Roman IAST.
            category_filter: Optional filter to restrict to specific Sandhi category.
            language: 'en' for English explanations, 'hi' for Hindi (हिंदी).

        Returns:
            SandhiResult containing combined word, applied rule, and bilingual explanation.
        """
        is_hi = (language == "hi")

        # Step 1: Input Validation
        if not word1_input or not word1_input.strip():
            err_en = "First word (Pūrva-pada) cannot be empty. Please provide two Sanskrit word-parts."
            err_hi = "प्रथम पद (पूर्वपदम्) रिक्त नहीं हो सकता। कृपया दो संस्कृत पद दर्ज करें।"
            return SandhiResult(
                status="error",
                word1="",
                word2=word2_input or "",
                combined="",
                error_message=err_hi if is_hi else err_en,
                error_message_en=err_en,
                error_message_hi=err_hi,
                language=language
            )

        if not word2_input or not word2_input.strip():
            err_en = "Second word (Uttara-pada) cannot be empty. Please provide two Sanskrit word-parts."
            err_hi = "द्वितीय पद (उत्तरपदम्) रिक्त नहीं हो सकता। कृपया दो संस्कृत पद दर्ज करें।"
            return SandhiResult(
                status="error",
                word1=word1_input or "",
                word2="",
                combined="",
                error_message=err_hi if is_hi else err_en,
                error_message_en=err_en,
                error_message_hi=err_hi,
                language=language
            )

        # Step 2: Normalization & Transliteration Detection
        w1_raw = word1_input.strip()
        w2_raw = word2_input.strip()

        # Check for Roman ambiguities
        ambiguity_warnings = []
        if not is_devanagari(w1_raw) or not is_devanagari(w2_raw):
            try:
                from transliteration import detect_ambiguities
                ambiguity_warnings = detect_ambiguities(w1_raw) + detect_ambiguities(w2_raw)
            except ImportError:
                pass

        # If input is Roman transliteration, convert to Devanagari
        w1_dev = w1_raw if is_devanagari(w1_raw) else roman_to_devanagari(w1_raw)
        w2_dev = w2_raw if is_devanagari(w2_raw) else roman_to_devanagari(w2_raw)

        w1 = normalize_sanskrit(w1_dev)
        w2 = normalize_sanskrit(w2_dev)

        w1_iast = devanagari_to_iast(w1)
        w2_iast = devanagari_to_iast(w2)

        # Step 3: Phoneme Boundary Decomposition
        p_stem, p_type, p_end, p_pre_vis = decompose_purva_pada(w1)
        u_start, u_is_vowel, u_rest = decompose_uttara_pada(w2)

        # Step 4: Rule Dispatch based on boundary characteristics
        res: Optional[SandhiResult] = None

        # A. Visarga Sandhi (विसर्गसन्धिः)
        if p_type == "visarga":
            res = self._check_visarga_sandhi(
                w1, w2, w1_iast, w2_iast, p_stem, p_pre_vis, u_start, u_is_vowel, u_rest
            )

        # B. Consonant Sandhi (व्यञ्जनसन्धिः / Hal Sandhi)
        elif p_type == "halanta":
            res = self._check_vyanjana_sandhi(
                w1, w2, w1_iast, w2_iast, p_stem, p_end, u_start, u_is_vowel, u_rest
            )

        # C. Vowel Sandhi (स्वरसन्धिः / Ac Sandhi)
        elif p_type == "vowel" and u_is_vowel:
            res = self._check_svara_sandhi(
                w1, w2, w1_iast, w2_iast, p_stem, p_end, u_start, u_rest
            )

        # D. Vowel followed by consonant (Normal Sanskrit juncture, no sandhi change)
        elif p_type == "vowel" and not u_is_vowel:
            # Standard juncture where vowel + consonant simply juxtapose
            combined = f"{w1} {w2}"
            bb_en = f"Ending vowel: '{p_end}' | Starting consonant: '{u_start}'"
            bb_hi = f"अन्त्य स्वर: '{p_end}' | आदिव्यञ्जन: '{u_start}'"
            exp_en = f"No Sandhi operation applies between a final vowel '{p_end}' and an initial consonant '{u_start}'. The two words remain separate."
            exp_hi = f"अन्त्य स्वर '{p_end}' तथा आदिव्यञ्जन '{u_start}' के मध्य कोई सन्धि-परिवर्तन नहीं होता। दोनों पद पृथक् रहते हैं।"
            return SandhiResult(
                status="no_sandhi",
                word1=w1,
                word2=w2,
                combined=combined,
                word1_iast=w1_iast,
                word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                boundary_breakdown=bb_hi if is_hi else bb_en,
                boundary_breakdown_en=bb_en,
                boundary_breakdown_hi=bb_hi,
                explanation=exp_hi if is_hi else exp_en,
                explanation_en=exp_en,
                explanation_hi=exp_hi,
                language=language,
                ambiguity_warnings=ambiguity_warnings
            )

        # Step 5: Check Category Filter if specified
        if res and res.status == "success" and category_filter and category_filter != "All":
            if category_filter.lower() not in res.category.lower():
                err_filter_en = (
                    f"The matched Sandhi rule '{res.rule_name}' belongs to '{res.category}', "
                    f"which does not match the chosen filter '{category_filter}'."
                )
                err_filter_hi = (
                    f"लागू होने वाला सन्धिनियम '{res.rule_name}' श्रेणी '{res.category}' का है, "
                    f"जो चयनित फ़िल्टर '{category_filter}' से मेल नहीं खाता।"
                )
                return SandhiResult(
                    status="unsupported",
                    word1=w1,
                    word2=w2,
                    combined="",
                    word1_iast=w1_iast,
                    word2_iast=w2_iast,
                    error_message=err_filter_hi if is_hi else err_filter_en,
                    error_message_en=err_filter_en,
                    error_message_hi=err_filter_hi,
                    language=language,
                    ambiguity_warnings=ambiguity_warnings
                )

        if res and res.status == "success":
            # Enrich with bilingual metadata from rules.json
            rule = self.rules_by_id.get(res.rule_id)
            if rule:
                res.rule_name_en = rule.get("rule_name_en", rule.get("rule_name", res.rule_name))
                res.rule_name_hi = rule.get("rule_name_hi", rule.get("rule_name", res.rule_name))
                res.category_en = rule.get("category_en", rule.get("category", res.category))
                res.category_hi = rule.get("category_hi", rule.get("category", res.category))
                res.explanation_en = rule.get("explanation_en", rule.get("explanation", res.explanation))
                res.explanation_hi = rule.get("explanation_hi", rule.get("explanation", res.explanation))
                res.transformation_detail_en = rule.get("transformation_en", rule.get("transformation", res.transformation_detail))
                res.transformation_detail_hi = rule.get("transformation_hi", rule.get("transformation", res.transformation_detail))
                if not res.boundary_breakdown_en:
                    res.boundary_breakdown_en = res.boundary_breakdown
                if not res.boundary_breakdown_hi:
                    res.boundary_breakdown_hi = res.boundary_breakdown

            res.ambiguity_warnings = ambiguity_warnings
            if is_hi:
                return res.localized("hi")
            return res

        # Step 6: Unsupported or Non-matching combination
        err_unsup_en = "No matching implemented Sandhi rule was found for these inputs. Please verify the Sanskrit word-parts or consult the Rule Knowledge Base."
        err_unsup_hi = "इन प्रविष्टियों के लिए कोई मान्य पाणिनीय सन्धिनियम नहीं मिला। कृपया संस्कृत पदों की शुद्धता की जाँच करें अथवा नियम-संग्रह (Knowledge Base) देखें।"
        bb_unsup_en = f"Pūrva boundary: {p_end} (type: {p_type}) | Uttara boundary: {u_start} ({'vowel' if u_is_vowel else 'consonant'})"
        bb_unsup_hi = f"पूर्वपद-अन्त्यवर्ण: {p_end} (प्रकार: {p_type}) | उत्तरपद-आदिवर्ण: {u_start} ({'स्वर' if u_is_vowel else 'व्यञ्जन'})"

        return SandhiResult(
            status="unsupported",
            word1=w1,
            word2=w2,
            combined="",
            word1_iast=w1_iast,
            word2_iast=w2_iast,
            boundary_breakdown=bb_unsup_hi if is_hi else bb_unsup_en,
            boundary_breakdown_en=bb_unsup_en,
            boundary_breakdown_hi=bb_unsup_hi,
            error_message=err_unsup_hi if is_hi else err_unsup_en,
            error_message_en=err_unsup_en,
            error_message_hi=err_unsup_hi,
            language=language,
            ambiguity_warnings=ambiguity_warnings
        )

    # -----------------------------------------------------------------------
    # 7. Svara Sandhi (स्वरसन्धिः / Vowel Sandhi) Module
    # -----------------------------------------------------------------------

    def _check_svara_sandhi(
        self,
        w1: str,
        w2: str,
        w1_iast: str,
        w2_iast: str,
        p_stem: str,
        v1: str,
        v2: str,
        rest2: str
    ) -> Optional[SandhiResult]:
        """
        Evaluate Svara Sandhi rules in authentic Paninian order of precedence:
        1. Pragṛhya / Prakṛtibhāva (1.1.11, 6.1.125)
        2. Pūrvarūpa Sandhi (6.1.109 - special exception to Ayādi)
        3. Dīrgha Sandhi (6.1.101 - Akaḥ savarṇe dīrghaḥ)
        4. Guṇa Sandhi (6.1.87 - Ādguṇaḥ)
        5. Vṛddhi Sandhi (6.1.88 - Vṛddhireci)
        6. Yaṇ Sandhi (6.1.77 - Iko yaṇaci)
        7. Ayādi Sandhi (6.1.78 - Eco'yavāyāvaḥ)
        """

        # 1. Prakṛtibhāva Sandhi (SVAR_07): Duals ending in ī, ū, e
        pragrhya_forms = {"हरी", "विष्णू", "गङ्गे", "कवी", "साधू", "लते"}
        if w1 in pragrhya_forms:
            rule = self.rules_by_id["SVAR_07"]
            combined = f"{w1} {w2}"
            return SandhiResult(
                status="success",
                word1=w1,
                word2=w2,
                combined=combined,
                word1_iast=w1_iast,
                word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"],
                rule_name=rule["rule_name"],
                category=rule["category"],
                sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{v1} + {v2} → {v1} {v2} (प्रकृतिभावः)",
                boundary_breakdown=f"{w1} [{v1}] + {w2} [{v2}] → {combined} (No sound merger)",
                explanation=rule["explanation"]
            )

        # 2. Pūrvarūpa Sandhi (SVAR_06) vs Ayādi Sandhi (SVAR_05) for e/o + short a
        # Sūtra 6.1.109 (Eṅaḥ padāntādati) applies only to padānta (inflected words).
        # Verbal roots/stems before suffixes like 'ana' (ne+ana -> nayana, po+ana -> pavana)
        # undergo Ayādi (6.1.78 Eco'yavāyāvaḥ).
        ayadi_stems = {"ने", "शे", "पो", "भो", "च्यो", "लो", "ह्वे"}
        is_ayadi_affix = w2 in ("अन", "अक", "अनम्", "अति")
        is_ayadi_case = (w1 in ayadi_stems) or is_ayadi_affix

        if v1 in ("ए", "ओ") and v2 == "अ" and not is_ayadi_case:
            rule = self.rules_by_id["SVAR_06"]
            # Word 1 stays intact; short 'a' of word 2 replaced by avagraha ऽ
            combined = f"{w1}ऽ{rest2}"
            return SandhiResult(
                status="success",
                word1=w1,
                word2=w2,
                combined=combined,
                word1_iast=w1_iast,
                word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"],
                rule_name=rule["rule_name"],
                category=rule["category"],
                sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{v1} + अ → {v1}ऽ (पूर्वरूपम् - एङः पदान्तादति)",
                boundary_breakdown=f"{w1} [{v1}] + {w2} [अ + {rest2}] → {w1} + ऽ{rest2} = {combined}",
                explanation=rule["explanation"]
            )

        # 3. Dīrgha Sandhi (SVAR_01): Akaḥ savarṇe dīrghaḥ (6.1.101)
        # Check if v1 and v2 belong to the same savarna vocalic family
        fam1 = SAVARNA_FAMILIES.get(v1)
        fam2 = SAVARNA_FAMILIES.get(v2)

        if fam1 and fam2 and fam1 == fam2:
            long_v = LONG_EQUIVALENT[fam1]
            combined = join_stem_with_vowel(p_stem, long_v) + rest2
            rule = self.rules_by_id["SVAR_01"]
            return SandhiResult(
                status="success",
                word1=w1,
                word2=w2,
                combined=combined,
                word1_iast=w1_iast,
                word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"],
                rule_name=rule["rule_name"],
                category=rule["category"],
                sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{v1} + {v2} → {long_v} (दीर्घः)",
                boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} + {v2} = {long_v} → {combined}",
                explanation=rule["explanation"]
            )

        # 4. Guṇa Sandhi (SVAR_02): a / ā followed by dissimilar simple vowel
        if v1 in ("अ", "आ"):
            if v2 in ("इ", "ई"):
                combined = join_stem_with_vowel(p_stem, "ए") + rest2
                rule = self.rules_by_id["SVAR_02"]
                return SandhiResult(
                    status="success",
                    word1=w1, word2=w2, combined=combined,
                    word1_iast=w1_iast, word2_iast=w2_iast,
                    combined_iast=devanagari_to_iast(combined),
                    rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                    category=rule["category"], sutra=rule["sutra"],
                    reference=rule["reference"],
                    transformation_detail=f"{v1} + {v2} → ए (गुणः)",
                    boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} + {v2} = ए → {combined}",
                    explanation=rule["explanation"]
                )
            elif v2 in ("उ", "ऊ"):
                combined = join_stem_with_vowel(p_stem, "ओ") + rest2
                rule = self.rules_by_id["SVAR_02"]
                return SandhiResult(
                    status="success",
                    word1=w1, word2=w2, combined=combined,
                    word1_iast=w1_iast, word2_iast=w2_iast,
                    combined_iast=devanagari_to_iast(combined),
                    rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                    category=rule["category"], sutra=rule["sutra"],
                    reference=rule["reference"],
                    transformation_detail=f"{v1} + {v2} → ओ (गुणः)",
                    boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} + {v2} = ओ → {combined}",
                    explanation=rule["explanation"]
                )
            elif v2 in ("ऋ", "ॠ"):
                # a/ā + ṛ/ṝ -> ar (अर्) by sūtra 1.1.51 Uraṇ raparaḥ
                combined = p_stem[:-1] + "र्" + rest2 if p_stem.endswith("्") else p_stem + "र्" + rest2
                rule = self.rules_by_id["SVAR_02"]
                return SandhiResult(
                    status="success",
                    word1=w1, word2=w2, combined=combined,
                    word1_iast=w1_iast, word2_iast=w2_iast,
                    combined_iast=devanagari_to_iast(combined),
                    rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                    category=rule["category"], sutra=rule["sutra"],
                    reference=rule["reference"],
                    transformation_detail=f"{v1} + {v2} → अर् (गुणः + उरण् रपरः)",
                    boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} + {v2} = अर् → {combined}",
                    explanation=rule["explanation"]
                )
            elif v2 == "ऌ":
                combined = p_stem[:-1] + "ल्" + rest2 if p_stem.endswith("्") else p_stem + "ल्" + rest2
                rule = self.rules_by_id["SVAR_02"]
                return SandhiResult(
                    status="success",
                    word1=w1, word2=w2, combined=combined,
                    word1_iast=w1_iast, word2_iast=w2_iast,
                    combined_iast=devanagari_to_iast(combined),
                    rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                    category=rule["category"], sutra=rule["sutra"],
                    reference=rule["reference"],
                    transformation_detail=f"{v1} + {v2} → अल् (गुणः)",
                    boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} + {v2} = अल् → {combined}",
                    explanation=rule["explanation"]
                )

        # 5. Vṛddhi Sandhi (SVAR_03): a / ā followed by diphthong (e, ai, o, au)
        if v1 in ("अ", "आ"):
            if v2 in ("ए", "ऐ"):
                combined = join_stem_with_vowel(p_stem, "ऐ") + rest2
                rule = self.rules_by_id["SVAR_03"]
                return SandhiResult(
                    status="success",
                    word1=w1, word2=w2, combined=combined,
                    word1_iast=w1_iast, word2_iast=w2_iast,
                    combined_iast=devanagari_to_iast(combined),
                    rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                    category=rule["category"], sutra=rule["sutra"],
                    reference=rule["reference"],
                    transformation_detail=f"{v1} + {v2} → ऐ (वृद्धिः)",
                    boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} + {v2} = ऐ → {combined}",
                    explanation=rule["explanation"]
                )
            elif v2 in ("ओ", "औ"):
                combined = join_stem_with_vowel(p_stem, "औ") + rest2
                rule = self.rules_by_id["SVAR_03"]
                return SandhiResult(
                    status="success",
                    word1=w1, word2=w2, combined=combined,
                    word1_iast=w1_iast, word2_iast=w2_iast,
                    combined_iast=devanagari_to_iast(combined),
                    rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                    category=rule["category"], sutra=rule["sutra"],
                    reference=rule["reference"],
                    transformation_detail=f"{v1} + {v2} → औ (वृद्धिः)",
                    boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} + {v2} = औ → {combined}",
                    explanation=rule["explanation"]
                )

        # 6. Yaṇ Sandhi (SVAR_04): Ik vowels followed by dissimilar vowel
        yan_map = {
            "इ": "य्", "ई": "य्",
            "उ": "व्", "ऊ": "व्",
            "ऋ": "र्", "ॠ": "र्",
            "ऌ": "ल्"
        }
        if v1 in yan_map:
            semivowel = yan_map[v1]
            stem_with_semi = (p_stem + semivowel) if p_stem else semivowel
            combined = join_stem_with_vowel(stem_with_semi, v2) + rest2
            rule = self.rules_by_id["SVAR_04"]
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{v1} → {semivowel} (यण्)",
                boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} becomes {semivowel} + {v2} → {combined}",
                explanation=rule["explanation"]
            )

        # 7. Ayādi Sandhi (SVAR_05): Ec vowels followed by any vowel
        ayadi_map = {
            "ए": ("अ", "य्"),
            "ओ": ("अ", "व्"),
            "ऐ": ("आ", "य्"),
            "औ": ("आ", "व्")
        }
        if v1 in ayadi_map:
            lead_v, glide = ayadi_map[v1]
            # Form base: stem + lead_v + glide
            first_part = join_stem_with_vowel(p_stem, lead_v) + glide
            combined = join_stem_with_vowel(first_part, v2) + rest2
            rule = self.rules_by_id["SVAR_05"]
            ayadi_name = f"{lead_v}{glide}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{v1} → {ayadi_name} (अयादिः)",
                boundary_breakdown=f"{w1} [{p_stem} + {v1}] + {w2} [{v2} + {rest2}] → {v1} becomes {ayadi_name} + {v2} → {combined}",
                explanation=rule["explanation"]
            )

        return None

    # -----------------------------------------------------------------------
    # 8. Vyañjana Sandhi (व्यञ्जनसन्धिः / Consonant Sandhi) Module
    # -----------------------------------------------------------------------

    def _check_vyanjana_sandhi(
        self,
        w1: str,
        w2: str,
        w1_iast: str,
        w2_iast: str,
        p_stem: str,
        c1: str,
        u_start: str,
        u_is_vowel: bool,
        u_rest: str
    ) -> Optional[SandhiResult]:
        """
        Evaluate Vyañjana Sandhi rules:
        1. Anusvāra Sandhi (8.3.23 - Mo'nusvāraḥ)
        2. Torli Sandhi (8.4.60 - Dental before 'l')
        3. Ścutva Sandhi (8.4.40 - Stoḥ ścunā ścuḥ)
        4. Ṣṭutva Sandhi (8.4.41 - Ṣṭunā ṣṭuḥ)
        5. Anunāsika Sandhi (8.4.45 - Stop before nasal)
        6. Cartva Sandhi (8.4.55 - Khari ca)
        7. Jaśtva Sandhi (8.2.39 - Jhalāṁ jaśo'nte)
        """

        # 1. Anusvāra Sandhi (VYAN_06): Word-final 'm' (म्) before consonant
        if c1 == "म्" and not u_is_vowel:
            rule = self.rules_by_id["VYAN_06"]
            combined = f"{p_stem}ं {w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail="म् + consonant → ं + consonant (अनुस्वारः)",
                boundary_breakdown=f"{w1} [म्] + {w2} [{u_start}] → {combined}",
                explanation=rule["explanation"]
            )

        # 2. Torli Parasavarṇa Sandhi (VYAN_07): Dental stop before 'l' (ल)
        if c1 in ("त्", "थ्", "द्", "ध्") and u_start == "ल":
            rule = self.rules_by_id["VYAN_07"]
            combined = f"{p_stem}ल्{w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{c1} + ल → ल्ल (तोर्लि परसवर्णः)",
                boundary_breakdown=f"{w1} [{c1}] + {w2} [ल] → {combined}",
                explanation=rule["explanation"]
            )

        # 3. Ścutva Sandhi (VYAN_01): Dental (s, t-varga) before Palatal (ś, c-varga)
        if c1 in DENTAL_TO_PALATAL and u_start in VARGA_CA + ["श"]:
            palatal_c = DENTAL_TO_PALATAL[c1]
            # Dental stops assimilate voicing of the following palatal stop:
            # t/th/d/dh before voiced palatal (j, jh) becomes voiced palatal 'j' (ज्)
            # t/th/d/dh before voiceless palatal (c, ch) becomes voiceless palatal 'c' (च्)
            if c1 in ("त्", "थ्", "द्", "ध्"):
                if u_start in ("ज", "झ"):
                    palatal_c = "ज्"
                elif u_start in ("च", "छ", "श"):
                    palatal_c = "च्"

            rule = self.rules_by_id["VYAN_01"]
            combined = f"{p_stem}{palatal_c}{w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{c1} → {palatal_c} (श्चुत्वम्)",
                boundary_breakdown=f"{w1} [{c1}] + {w2} [{u_start}] → {c1} changes to {palatal_c} → {combined}",
                explanation=rule["explanation"]
            )

        # 4. Ṣṭutva Sandhi (VYAN_02): Dental before Retroflex (ṣ, ṭ-varga)
        if c1 in DENTAL_TO_RETROFLEX and u_start in VARGA_TA_RETRO + ["ष"]:
            retro_c = DENTAL_TO_RETROFLEX[c1]
            rule = self.rules_by_id["VYAN_02"]
            combined = f"{p_stem}{retro_c}{w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{c1} → {retro_c} (ष्टुत्वम्)",
                boundary_breakdown=f"{w1} [{c1}] + {w2} [{u_start}] → {c1} changes to {retro_c} → {combined}",
                explanation=rule["explanation"]
            )

        # 5. Anunāsika Sandhi (VYAN_05): Stop before Nasal consonant (m, n)
        if c1 in STOP_TO_NASAL and u_start in NASALS:
            nasal_c = STOP_TO_NASAL[c1]
            rule = self.rules_by_id["VYAN_05"]
            combined = f"{p_stem}{nasal_c}{w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{c1} → {nasal_c} (अनुनासिकः)",
                boundary_breakdown=f"{w1} [{c1}] + {w2} [{u_start}] → {c1} changes to {nasal_c} → {combined}",
                explanation=rule["explanation"]
            )

        # 6. Cartva Sandhi (VYAN_04): Voiced stop before Voiceless consonant (khar)
        if c1 in VOICED_TO_FIRST and u_start in VOICELESS_CONSONANTS:
            voiceless_c = VOICED_TO_FIRST[c1]
            rule = self.rules_by_id["VYAN_04"]
            combined = f"{p_stem}{voiceless_c}{w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{c1} → {voiceless_c} (चर्त्वम्)",
                boundary_breakdown=f"{w1} [{c1}] + {w2} [{u_start}] → {c1} changes to {voiceless_c} → {combined}",
                explanation=rule["explanation"]
            )

        # 7. Jaśtva Sandhi (VYAN_03): Final stop before Vowel or Voiced Consonant
        if c1 in STOP_TO_THIRD and (u_is_vowel or u_start in VOICED_CONSONANTS):
            third_c = STOP_TO_THIRD[c1]
            rule = self.rules_by_id["VYAN_03"]
            if u_is_vowel:
                # Merge the 3rd consonant with the following vowel
                stem_merged = join_stem_with_vowel(f"{p_stem}{third_c}", u_start)
                combined = f"{stem_merged}{u_rest}"
            else:
                combined = f"{p_stem}{third_c}{w2}"

            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{c1} → {third_c} (जश्त्वम्)",
                boundary_breakdown=f"{w1} [{c1}] + {w2} [{u_start}] → {c1} changes to {third_c} → {combined}",
                explanation=rule["explanation"]
            )

        return None

    # -----------------------------------------------------------------------
    # 9. Visarga Sandhi (विसर्गसन्धिः) Module
    # -----------------------------------------------------------------------

    def _check_visarga_sandhi(
        self,
        w1: str,
        w2: str,
        w1_iast: str,
        w2_iast: str,
        p_stem: str,
        pre_v: Optional[str],
        u_start: str,
        u_is_vowel: bool,
        u_rest: str
    ) -> Optional[SandhiResult]:
        """
        Evaluate Visarga Sandhi rules:
        1. Visarga Lopa Sandhi (8.3.17, 8.3.19, 6.1.132)
        2. Utva Sandhi before short a (6.1.113 - Ato roraplutādaplutep)
        3. Utva Sandhi before voiced consonant (6.1.114 - Haśi ca)
        4. Visarga Sibilant Sandhi (8.3.34 - Visarjanīyasya saḥ)
        5. Rutva Sandhi (8.2.66 - Sasajuṣo ruḥ)
        """

        # 1. Visarga Lopa Sandhi (VIS_05)
        # Condition A: सः / एषः before any consonant
        if w1 in ("सः", "एषः") and not u_is_vowel:
            rule = self.rules_by_id["VIS_05"]
            w1_lopa = w1[:-1] # drops visarga: स or एष
            combined = f"{w1_lopa} {w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail="सः/एषः + consonant → स/एष (सुलोपः 6.1.132)",
                boundary_breakdown=f"{w1} + {w2} → Visarga elided → {combined}",
                explanation=rule["explanation"]
            )

        # Condition B: āḥ (आः) before any vowel or voiced consonant
        if pre_v == "आ" and (u_is_vowel or u_start in VOICED_CONSONANTS):
            rule = self.rules_by_id["VIS_05"]
            w1_lopa = w1[:-1] # 'बालाः' -> 'बाला'
            combined = f"{w1_lopa} {w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail="आः + vowel/voiced → आ (विसर्गलोपः)",
                boundary_breakdown=f"{w1} [आः] + {w2} [{u_start}] → Visarga elided → {combined}",
                explanation=rule["explanation"]
            )

        # Condition C: aḥ (अः) before any vowel other than short 'a'
        if pre_v == "अ" and u_is_vowel and u_start != "अ":
            rule = self.rules_by_id["VIS_05"]
            w1_lopa = w1[:-1] # 'रामः' -> 'राम'
            combined = f"{w1_lopa} {w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail="अः + non-a vowel → अ (विसर्गलोपः)",
                boundary_breakdown=f"{w1} [अः] + {w2} [{u_start}] → Visarga elided → {combined}",
                explanation=rule["explanation"]
            )

        # 2. Utva Sandhi before Short A (VIS_01): Ato roraplutādaplutep (6.1.113)
        if pre_v == "अ" and u_is_vowel and u_start == "अ":
            rule = self.rules_by_id["VIS_01"]
            # aḥ + a -> o + ऽ
            stem_o = join_stem_with_vowel(p_stem, "ओ")
            combined = f"{stem_o}ऽ{u_rest}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail="अः + अ → ोऽ (उत्वम् + पूर्वरूपम्)",
                boundary_breakdown=f"{w1} [अः] + {w2} [अ + {u_rest}] → {stem_o} + ऽ{u_rest} = {combined}",
                explanation=rule["explanation"]
            )

        # 3. Utva Sandhi before Voiced Consonants (VIS_02): Haśi ca (6.1.114)
        if pre_v == "अ" and not u_is_vowel and u_start in VOICED_CONSONANTS:
            rule = self.rules_by_id["VIS_02"]
            stem_o = join_stem_with_vowel(p_stem, "ओ")
            combined = f"{stem_o} {w2}"
            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail="अः + voiced consonant → ो + consonant (उत्वम् - हशि च)",
                boundary_breakdown=f"{w1} [अः] + {w2} [{u_start}] → {stem_o} + {w2} = {combined}",
                explanation=rule["explanation"]
            )

        # 4. Visarga Sibilant Sandhi (VIS_03): Visarjanīyasya saḥ (8.3.34)
        # ḥ + c/ch -> ś (श्); ḥ + ṭ/ṭh -> ṣ (ष्); ḥ + t/th -> s (स्)
        if not u_is_vowel:
            sibilant = None
            if u_start in ("च", "छ"):
                sibilant = "श्"
            elif u_start in ("ट", "ठ"):
                sibilant = "ष्"
            elif u_start in ("त", "थ"):
                sibilant = "स्"

            if sibilant:
                rule = self.rules_by_id["VIS_03"]
                combined = f"{w1[:-1]}{sibilant}{w2}"
                return SandhiResult(
                    status="success",
                    word1=w1, word2=w2, combined=combined,
                    word1_iast=w1_iast, word2_iast=w2_iast,
                    combined_iast=devanagari_to_iast(combined),
                    rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                    category=rule["category"], sutra=rule["sutra"],
                    reference=rule["reference"],
                    transformation_detail=f"ः + {u_start} → {sibilant}{u_start} (सत्वम्)",
                    boundary_breakdown=f"{w1} [ः] + {w2} [{u_start}] → ः becomes {sibilant} → {combined}",
                    explanation=rule["explanation"]
                )

        # 5. Rutva Sandhi (VIS_04): Sasajuṣo ruḥ (8.2.66)
        # Preceded by non-a/ā vowel, followed by vowel or voiced consonant
        if pre_v not in ("अ", "आ") and (u_is_vowel or u_start in VOICED_CONSONANTS):
            rule = self.rules_by_id["VIS_04"]
            base_w1 = w1[:-1] # drop visarga, keeping previous vowel, e.g. 'हरि', 'गुरु', 'मुनि'

            if u_is_vowel:
                # Merge 'र्' with the succeeding vowel:
                # e.g. 'हरि' + 'र्' + 'आ' = 'हरिरा'
                r_vowel = join_stem_with_vowel("र्", u_start)
                combined = f"{base_w1}{r_vowel}{u_rest}"
            else:
                # Preceding 'र्' before consonant forms repha:
                combined = f"{base_w1}र्{w2}"

            return SandhiResult(
                status="success",
                word1=w1, word2=w2, combined=combined,
                word1_iast=w1_iast, word2_iast=w2_iast,
                combined_iast=devanagari_to_iast(combined),
                rule_id=rule["rule_id"], rule_name=rule["rule_name"],
                category=rule["category"], sutra=rule["sutra"],
                reference=rule["reference"],
                transformation_detail=f"{pre_v}ः + {u_start} → {pre_v}र् + {u_start} (रुत्वम्)",
                boundary_breakdown=f"{w1} [{pre_v}ः] + {w2} [{u_start}] → ः becomes repha (र्) → {combined}",
                explanation=rule["explanation"]
            )

        return None
