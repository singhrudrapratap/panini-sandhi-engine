# -*- coding: utf-8 -*-
"""
=============================================================================
Comprehensive Automated Test Suite: Pāṇini Vyākaraṇa Sandhi Rule Engine
=============================================================================

Tests:
1. Rule loading and JSON configuration integrity
2. Verified classical examples from Pāṇini's Aṣṭādhyāyī across:
   - Svara Sandhi (Dīrgha, Guṇa, Vṛddhi, Yaṇ, Ayādi, Pūrvarūpa, Prakṛtibhāva)
   - Vyañjana Sandhi (Ścutva, Ṣṭutva, Jaśtva, Cartva, Anunāsika, Anusvāra, Torli)
   - Visarga Sandhi (Utva before 'a', Utva before voiced, Satva, Rutva, Lopa)
3. Edge cases: Empty inputs, leading/trailing whitespace, newlines
4. Unsupported / Invalid combinations (safe failure, no false positives)
5. Unicode preservation (NFC, avagraha, virama, matras, visarga)
6. Bidirectional Roman transliteration (IAST, Harvard-Kyoto)
7. Category filtering behavior
=============================================================================
"""

import os
import sys

# Ensure parent directory of tests is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

import pytest
from sandhi_engine import (
    PaniniSandhiEngine,
    SandhiResult,
    devanagari_to_iast,
    roman_to_devanagari,
    normalize_sanskrit,
    is_devanagari
)
from transliteration import (
    devanagari_to_harvard_kyoto,
    detect_script,
    detect_ambiguities,
    get_transliteration_reference_table
)

# Determine path to rules.json relative to tests directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(CURRENT_DIR, "..", "rules.json")


@pytest.fixture(scope="module")
def engine():
    """Fixture providing an initialized PaniniSandhiEngine instance."""
    return PaniniSandhiEngine(RULES_FILE)


# ---------------------------------------------------------------------------
# 1. Rule Loading and Database Integrity Tests
# ---------------------------------------------------------------------------

def test_engine_initialization(engine):
    """Verify that rules.json is loaded and contains all verified rules."""
    assert engine is not None
    assert len(engine.rules_list) >= 19
    categories = engine.get_categories()
    assert "Svara Sandhi (स्वरसन्धिः)" in categories
    assert "Vyañjana Sandhi (व्यञ्जनसन्धिः)" in categories
    assert "Visarga Sandhi (विसर्गसन्धिः)" in categories


def test_rule_schema_completeness(engine):
    """Ensure every rule has all mandatory metadata fields required by specifications."""
    mandatory_fields = [
        "rule_id", "rule_name", "category", "sutra",
        "reference", "description", "transformation",
        "explanation", "examples"
    ]
    for rule in engine.rules_list:
        for field in mandatory_fields:
            assert field in rule, f"Rule {rule.get('rule_id')} missing field: {field}"
        assert len(rule["examples"]) >= 1, f"Rule {rule['rule_id']} has no worked examples!"


def test_missing_rules_file_raises_error():
    """Verify that a non-existent rules file triggers FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        PaniniSandhiEngine("non_existent_rules_path.json")


# ---------------------------------------------------------------------------
# 2. Comprehensive Parametrized Classical Examples Test
# ---------------------------------------------------------------------------

def get_all_classical_examples():
    """Load all examples from the rules file to test dynamically."""
    temp_engine = PaniniSandhiEngine(RULES_FILE)
    return temp_engine.get_all_examples()


@pytest.mark.parametrize(
    "example",
    get_all_classical_examples(),
    ids=lambda ex: f"{ex['rule_id']}_{ex['word1']}+{ex['word2']}"
)
def test_all_verified_examples_from_database(engine, example):
    """
    Every verified classical example recorded in rules.json must execute
    with status='success' and produce the authoritative combined form.
    """
    w1 = example["word1"]
    w2 = example["word2"]
    expected_combined = example["combined"]

    result = engine.analyze(w1, w2)

    assert result.status == "success", (
        f"Failed to match rule for: {w1} + {w2}. "
        f"Error: {result.error_message}"
    )
    assert result.combined == expected_combined, (
        f"Mismatch in combined output for {w1} + {w2}: "
        f"Got '{result.combined}', expected '{expected_combined}'"
    )
    assert result.rule_id == example["rule_id"], (
        f"Wrong rule matched for {w1} + {w2}: "
        f"Got '{result.rule_id}', expected '{example['rule_id']}'"
    )


# ---------------------------------------------------------------------------
# 3. Individual Svara Sandhi Rule Tests (स्वरसन्धिः)
# ---------------------------------------------------------------------------

class TestSvaraSandhi:
    """Detailed unit tests for Vowel Sandhi rules."""

    def test_dirgha_sandhi_a(self, engine):
        """Dīrgha: a + ā -> ā (Aṣṭādhyāyī 6.1.101)"""
        res = engine.analyze("हिम", "आलय")
        assert res.status == "success"
        assert res.combined == "हिमालय"
        assert res.rule_id == "SVAR_01"

    def test_dirgha_sandhi_i(self, engine):
        """Dīrgha: i + ī -> ī (Aṣṭādhyāyī 6.1.101)"""
        res = engine.analyze("कपि", "ईश")
        assert res.status == "success"
        assert res.combined == "कपीश"
        assert res.rule_id == "SVAR_01"

    def test_dirgha_sandhi_u(self, engine):
        """Dīrgha: u + u -> ū (Aṣṭādhyāyī 6.1.101)"""
        res = engine.analyze("भानु", "उदय")
        assert res.status == "success"
        assert res.combined == "भानूदय"
        assert res.rule_id == "SVAR_01"

    def test_dirgha_sandhi_r(self, engine):
        """Dīrgha: ṛ + ṛ -> ṝ (Aṣṭādhyāyī 6.1.101)"""
        res = engine.analyze("पितृ", "ऋणम्")
        assert res.status == "success"
        assert res.combined == "पितॄणम्"
        assert res.rule_id == "SVAR_01"

    def test_guna_sandhi_e(self, engine):
        """Guṇa: a + ī -> e (Aṣṭādhyāyī 6.1.87)"""
        res = engine.analyze("नर", "ईश")
        assert res.status == "success"
        assert res.combined == "नरेश"
        assert res.rule_id == "SVAR_02"

    def test_guna_sandhi_o(self, engine):
        """Guṇa: ā + u -> o (Aṣṭādhyāyī 6.1.87)"""
        res = engine.analyze("महा", "उत्सव")
        assert res.status == "success"
        assert res.combined == "महोत्सव"
        assert res.rule_id == "SVAR_02"

    def test_guna_sandhi_ar(self, engine):
        """Guṇa: ā + ṛ -> ar (Aṣṭādhyāyī 6.1.87 + 1.1.51)"""
        res = engine.analyze("महा", "ऋषि")
        assert res.status == "success"
        assert res.combined == "महर्षि"
        assert res.rule_id == "SVAR_02"

    def test_guna_sandhi_al(self, engine):
        """Guṇa: a + ḷ -> al (Aṣṭādhyāyī 6.1.87)"""
        res = engine.analyze("तव", "ऌकार")
        assert res.status == "success"
        assert res.combined == "तवल्कार"
        assert res.rule_id == "SVAR_02"

    def test_vriddhi_sandhi_ai(self, engine):
        """Vṛddhi: ā + e -> ai (Aṣṭādhyāyī 6.1.88)"""
        res = engine.analyze("सदा", "एव")
        assert res.status == "success"
        assert res.combined == "सदैव"
        assert res.rule_id == "SVAR_03"

    def test_vriddhi_sandhi_au(self, engine):
        """Vṛddhi: a + o -> au (Aṣṭādhyāyī 6.1.88)"""
        res = engine.analyze("जल", "ओघ")
        assert res.status == "success"
        assert res.combined == "जलौघ"
        assert res.rule_id == "SVAR_03"

    def test_yan_sandhi_y(self, engine):
        """Yaṇ: i + ā -> yā (Aṣṭādhyāyī 6.1.77)"""
        res = engine.analyze("इति", "आदि")
        assert res.status == "success"
        assert res.combined == "इत्यादि"
        assert res.rule_id == "SVAR_04"

    def test_yan_sandhi_v(self, engine):
        """Yaṇ: u + ā -> vā (Aṣṭādhyāyī 6.1.77)"""
        res = engine.analyze("सु", "आगतम्")
        assert res.status == "success"
        assert res.combined == "स्वागतम्"
        assert res.rule_id == "SVAR_04"

    def test_yan_sandhi_r(self, engine):
        """Yaṇ: ṛ + ā -> rā (Aṣṭādhyāyī 6.1.77)"""
        res = engine.analyze("पितृ", "आज्ञा")
        assert res.status == "success"
        assert res.combined == "पित्राज्ञा"
        assert res.rule_id == "SVAR_04"

    def test_ayadi_sandhi_ay(self, engine):
        """Ayādi: e + a -> ay (Aṣṭādhyāyī 6.1.78)"""
        res = engine.analyze("ने", "अन")
        assert res.status == "success"
        assert res.combined == "नयन"
        assert res.rule_id == "SVAR_05"

    def test_ayadi_sandhi_av(self, engine):
        """Ayādi: o + a -> av (Aṣṭādhyāyī 6.1.78)"""
        res = engine.analyze("पो", "अन")
        assert res.status == "success"
        assert res.combined == "पवन"
        assert res.rule_id == "SVAR_05"

    def test_ayadi_sandhi_aay(self, engine):
        """Ayādi: ai + a -> āy (Aṣṭādhyāyī 6.1.78)"""
        res = engine.analyze("नै", "अक")
        assert res.status == "success"
        assert res.combined == "नायक"
        assert res.rule_id == "SVAR_05"

    def test_ayadi_sandhi_aav(self, engine):
        """Ayādi: au + a -> āv (Aṣṭādhyāyī 6.1.78)"""
        res = engine.analyze("पौ", "अक")
        assert res.status == "success"
        assert res.combined == "पावक"
        assert res.rule_id == "SVAR_05"

    def test_purvarupa_sandhi(self, engine):
        """Pūrvarūpa: e + a -> e' (Aṣṭādhyāyī 6.1.109)"""
        res = engine.analyze("ते", "अपि")
        assert res.status == "success"
        assert res.combined == "तेऽपि"
        assert res.rule_id == "SVAR_06"

    def test_prakrtibhava_sandhi(self, engine):
        """Prakṛtibhāva: Dual pragṛhya unchanged (1.1.11, 6.1.125)"""
        res = engine.analyze("हरी", "एतौ")
        assert res.status == "success"
        assert res.combined == "हरी एतौ"
        assert res.rule_id == "SVAR_07"


# ---------------------------------------------------------------------------
# 4. Individual Vyañjana Sandhi Rule Tests (व्यञ्जनसन्धिः)
# ---------------------------------------------------------------------------

class TestVyanjanaSandhi:
    """Detailed unit tests for Consonant Sandhi rules."""

    def test_scutva_sandhi_t_c(self, engine):
        """Ścutva: t + c -> cc (Aṣṭādhyāyī 8.4.40)"""
        res = engine.analyze("सत्", "चित्")
        assert res.status == "success"
        assert res.combined == "सच्चित्"
        assert res.rule_id == "VYAN_01"

    def test_scutva_sandhi_t_j(self, engine):
        """Ścutva: t + j -> jj (Aṣṭādhyāyī 8.4.40)"""
        res = engine.analyze("सत्", "जन")
        assert res.status == "success"
        assert res.combined == "सज्जन"
        assert res.rule_id == "VYAN_01"

    def test_stutva_sandhi(self, engine):
        """Ṣṭutva: t + ṭ -> ṭṭ (Aṣṭādhyāyī 8.4.41)"""
        res = engine.analyze("तत्", "टीका")
        assert res.status == "success"
        assert res.combined == "तट्टीका"
        assert res.rule_id == "VYAN_02"

    def test_jastva_sandhi_vowel(self, engine):
        """Jaśtva: k + ī -> gī (Aṣṭādhyāyī 8.2.39)"""
        res = engine.analyze("वाक्", "ईश")
        assert res.status == "success"
        assert res.combined == "वागीश"
        assert res.rule_id == "VYAN_03"

    def test_jastva_sandhi_voiced_cons(self, engine):
        """Jaśtva: k + g -> gg (Aṣṭādhyāyī 8.2.39)"""
        res = engine.analyze("दिक्", "गज")
        assert res.status == "success"
        assert res.combined == "दिग्गज"
        assert res.rule_id == "VYAN_03"

    def test_cartva_sandhi(self, engine):
        """Cartva: d + k -> tk (Aṣṭādhyāyī 8.4.55)"""
        res = engine.analyze("सद्", "कार")
        assert res.status == "success"
        assert res.combined == "सत्कार"
        assert res.rule_id == "VYAN_04"

    def test_anunasika_sandhi(self, engine):
        """Anunāsika: t + n -> nn (Aṣṭādhyāyī 8.4.45)"""
        res = engine.analyze("जगत्", "नाथ")
        assert res.status == "success"
        assert res.combined == "जगन्नाथ"
        assert res.rule_id == "VYAN_05"

    def test_anusvara_sandhi(self, engine):
        """Anusvāra: m + cons -> ṁ cons (Aṣṭādhyāyī 8.3.23)"""
        res = engine.analyze("हरिम्", "वन्दे")
        assert res.status == "success"
        assert res.combined == "हरिं वन्दे"
        assert res.rule_id == "VYAN_06"

    def test_torli_sandhi(self, engine):
        """Torli: t + l -> ll (Aṣṭādhyāyī 8.4.60)"""
        res = engine.analyze("तत्", "लय")
        assert res.status == "success"
        assert res.combined == "तल्लय"
        assert res.rule_id == "VYAN_07"


# ---------------------------------------------------------------------------
# 5. Individual Visarga Sandhi Rule Tests (विसर्गसन्धिः)
# ---------------------------------------------------------------------------

class TestVisargaSandhi:
    """Detailed unit tests for Visarga Sandhi rules."""

    def test_utva_before_short_a(self, engine):
        """Utva before 'a': aḥ + a -> o' (Aṣṭādhyāyī 6.1.113)"""
        res = engine.analyze("रामः", "अवदत्")
        assert res.status == "success"
        assert res.combined == "रामोऽवदत्"
        assert res.rule_id == "VIS_01"

    def test_utva_before_voiced_consonant(self, engine):
        """Utva before voiced cons: aḥ + g -> o g (Aṣṭādhyāyī 6.1.114)"""
        res = engine.analyze("रामः", "गच्छति")
        assert res.status == "success"
        assert res.combined == "रामो गच्छति"
        assert res.rule_id == "VIS_02"

    def test_satva_before_t(self, engine):
        """Satva before 't': ḥ + t -> st (Aṣṭādhyāyī 8.3.34)"""
        res = engine.analyze("नमः", "ते")
        assert res.status == "success"
        assert res.combined == "नमस्ते"
        assert res.rule_id == "VIS_03"

    def test_satva_before_c(self, engine):
        """Satva before 'c': ḥ + c -> śc (Aṣṭādhyāyī 8.3.34 + 8.4.40)"""
        res = engine.analyze("कः", "चित्")
        assert res.status == "success"
        assert res.combined == "कश्चित्"
        assert res.rule_id == "VIS_03"

    def test_rutva_before_vowel(self, engine):
        """Rutva before vowel: iḥ + ā -> irā (Aṣṭādhyāyī 8.2.66)"""
        res = engine.analyze("हरिः", "आगच्छति")
        assert res.status == "success"
        assert res.combined == "हरिरागच्छति"
        assert res.rule_id == "VIS_04"

    def test_rutva_before_voiced_cons(self, engine):
        """Rutva before voiced cons: iḥ + g -> irg (Aṣṭādhyāyī 8.2.66)"""
        res = engine.analyze("मुनिः", "गच्छति")
        assert res.status == "success"
        assert res.combined == "मुनिर्गच्छति"
        assert res.rule_id == "VIS_04"

    def test_visarga_lopa_ah_vowel(self, engine):
        """Visarga Lopa: āḥ drops before vowel/voiced (8.3.17)"""
        res = engine.analyze("बालाः", "नमन्ति")
        assert res.status == "success"
        assert res.combined == "बाला नमन्ति"
        assert res.rule_id == "VIS_05"

    def test_visarga_lopa_sah_cons(self, engine):
        """Visarga Lopa: saḥ drops before consonant (6.1.132)"""
        res = engine.analyze("सः", "गच्छति")
        assert res.status == "success"
        assert res.combined == "स गच्छति"
        assert res.rule_id == "VIS_05"


# ---------------------------------------------------------------------------
# 6. Robustness, Edge Cases, and Input Validation Tests
# ---------------------------------------------------------------------------

class TestEdgeCasesAndValidation:
    """Tests for edge cases, whitespace, empty strings, and malformed inputs."""

    def test_empty_word1(self, engine):
        """Word 1 is empty."""
        res = engine.analyze("", "आलय")
        assert res.status == "error"
        assert "empty" in res.error_message.lower()

    def test_empty_word2(self, engine):
        """Word 2 is empty."""
        res = engine.analyze("हिम", "")
        assert res.status == "error"
        assert "empty" in res.error_message.lower()

    def test_both_words_empty(self, engine):
        """Both inputs are empty strings."""
        res = engine.analyze("", "")
        assert res.status == "error"

    def test_whitespace_tolerance(self, engine):
        """Inputs with leading, trailing, and internal tabs/spaces."""
        res = engine.analyze("  हिम   ", "  \tआलय  \n")
        assert res.status == "success"
        assert res.combined == "हिमालय"

    def test_unsupported_combination(self, engine):
        """
        Arbitrary sound sequence with no valid Paninian sandhi rule.
        Must return status='unsupported' without crashing or fabricating results.
        """
        res = engine.analyze("वाक्", "प")
        # 'k' before voiceless 'p' remains without sandhi change in standard external sandhi
        # Engine should report safely without inventing a false merger.
        assert res.status in ("unsupported", "no_sandhi")

    def test_vowel_followed_by_consonant_no_sandhi(self, engine):
        """Vowel followed by consonant does not fuse arbitrarily."""
        res = engine.analyze("हिम", "कण")
        assert res.status == "no_sandhi"
        assert res.combined == "हिम कण"


# ---------------------------------------------------------------------------
# 7. Unicode and Devanagari Integrity Tests
# ---------------------------------------------------------------------------

class TestUnicodeIntegrity:
    """Verify Devanagari Unicode preservation."""

    def test_nfc_normalization(self):
        """Unicode NFC normalization preserves characters."""
        raw = "विद्य\u093e" # decomposed vs composed
        norm = normalize_sanskrit(raw)
        assert norm == "विद्या"

    def test_is_devanagari_detection(self):
        """Script detection accurately identifies Devanagari vs Roman."""
        assert is_devanagari("हिम") is True
        assert is_devanagari("hima") is False
        assert is_devanagari("123") is False


# ---------------------------------------------------------------------------
# 8. Transliteration (IAST & Harvard-Kyoto) Support Tests
# ---------------------------------------------------------------------------

class TestTransliteration:
    """Verify bidirectional transliteration and Roman input support."""

    def test_roman_iast_input_analysis(self, engine):
        """Users can input Roman IAST directly and receive accurate analysis."""
        res = engine.analyze("hima", "ālaya")
        assert res.status == "success"
        assert res.combined == "हिमालय"
        assert res.combined_iast == "himālaya"

    def test_harvard_kyoto_input_analysis(self, engine):
        """Users can input Harvard-Kyoto ASCII directly."""
        res = engine.analyze("hima", "Alaya")
        assert res.status == "success"
        assert res.combined == "हिमालय"

    def test_sat_cit_in_roman(self, engine):
        """Vyañjana sandhi with Roman input: sat + cit -> saccit."""
        res = engine.analyze("sat", "cit")
        assert res.status == "success"
        assert res.combined == "सच्चित्"
        assert res.combined_iast == "saccit"

    def test_namas_te_in_roman(self, engine):
        """Visarga sandhi with Roman input: namaḥ + te -> namaste."""
        res = engine.analyze("namaḥ", "te")
        assert res.status == "success"
        assert res.combined == "नमस्ते"
        assert res.combined_iast == "namaste"


# ---------------------------------------------------------------------------
# 9. Category Filtering Tests
# ---------------------------------------------------------------------------

class TestCategoryFilter:
    """Verify category selector filtering behavior."""

    def test_category_filter_matching(self, engine):
        """Matching category filter succeeds."""
        res = engine.analyze("हिम", "आलय", category_filter="Svara Sandhi")
        assert res.status == "success"
        assert res.rule_id == "SVAR_01"

    def test_category_filter_mismatch(self, engine):
        """Mismatched category filter reports appropriate notice."""
        res = engine.analyze("हिम", "आलय", category_filter="Visarga Sandhi")
        assert res.status == "unsupported"
        assert "filter" in res.error_message.lower()


# ---------------------------------------------------------------------------
# 10. Dedicated Transliteration Module Tests
# ---------------------------------------------------------------------------

class TestDedicatedTransliterationModule:
    """Comprehensive unit tests for transliteration.py standalone module."""

    def test_devanagari_to_iast_vowels(self):
        """Test Devanagari to IAST conversion for independent vowels and matras."""
        assert devanagari_to_iast("अ") == "a"
        assert devanagari_to_iast("आ") == "ā"
        assert devanagari_to_iast("इ") == "i"
        assert devanagari_to_iast("ई") == "ī"
        assert devanagari_to_iast("उ") == "u"
        assert devanagari_to_iast("ऊ") == "ū"
        assert devanagari_to_iast("ऋ") == "ṛ"
        assert devanagari_to_iast("ए") == "e"
        assert devanagari_to_iast("ऐ") == "ai"
        assert devanagari_to_iast("ओ") == "o"
        assert devanagari_to_iast("औ") == "au"

    def test_devanagari_to_iast_conjuncts_and_aspirates(self):
        """Test Devanagari to IAST for aspirated consonants, halanta, and conjuncts."""
        assert devanagari_to_iast("धर्म") == "dharma"
        assert devanagari_to_iast("सच्चित्") == "saccit"
        assert devanagari_to_iast("रामेश्वर") == "rāmeśvara"
        assert devanagari_to_iast("नमस्ते") == "namaste"
        assert devanagari_to_iast("रामोऽवदत्") == "rāmo'vadat"
        assert devanagari_to_iast("कण्ठ") == "kaṇṭha"
        assert devanagari_to_iast("शङ्ख") == "śaṅkha"

    def test_roman_to_devanagari_iast(self):
        """Test Roman IAST to Devanagari script conversion."""
        assert roman_to_devanagari("rāma") == "राम"
        assert roman_to_devanagari("īśvara") == "ईश्वर"
        assert roman_to_devanagari("rāmeśvara") == "रामेश्वर"
        assert roman_to_devanagari("saccit") == "सच्चित्"
        assert roman_to_devanagari("himālaya") == "हिमालय"
        assert roman_to_devanagari("vidyā") == "विद्या"

    def test_roman_to_devanagari_harvard_kyoto(self):
        """Test Harvard-Kyoto ASCII transliteration to Devanagari conversion."""
        assert roman_to_devanagari("hima") == "हिम"
        assert roman_to_devanagari("Alaya") == "आलय"
        assert roman_to_devanagari("Izvara") == "ईश्वर"
        assert roman_to_devanagari("deva") == "देव"

    def test_detect_script(self):
        """Test script detection between Devanagari and Roman."""
        assert detect_script("राम") == "devanagari"
        assert detect_script("विद्या") == "devanagari"
        assert detect_script("rāma") == "roman"
        assert detect_script("hima") == "roman"

    def test_detect_ambiguities_sh(self):
        """Detect ambiguous ASCII 'sh' (could be ś/श or ṣ/ष)."""
        warnings = detect_ambiguities("shiva")
        assert len(warnings) >= 1
        patterns = [w["pattern"] for w in warnings]
        assert "sh" in patterns

    def test_detect_ambiguities_ch(self):
        """Detect ambiguous ASCII 'ch' (in IAST 'c' is च and 'ch' is छ)."""
        warnings = detect_ambiguities("chatur")
        assert len(warnings) >= 1
        patterns = [w["pattern"] for w in warnings]
        assert "ch" in patterns

    def test_detect_ambiguities_plain_ascii_vowels(self):
        """Detect plain ASCII vowels in common words missing diacritics."""
        warnings = detect_ambiguities("rama")
        assert len(warnings) >= 1
        patterns = [w["pattern"] for w in warnings]
        assert "rama" in patterns

    def test_detect_ambiguities_clean_iast_no_warning(self):
        """Properly diacriticized IAST produces no ambiguity warnings."""
        warnings = detect_ambiguities("rāma")
        assert len(warnings) == 0

    def test_devanagari_input_no_ambiguity_warning(self):
        """Devanagari inputs produce zero ambiguity warnings."""
        warnings = detect_ambiguities("राम")
        assert len(warnings) == 0

    def test_get_transliteration_reference_table(self):
        """Reference table contains rich documentation data."""
        table = get_transliteration_reference_table()
        assert isinstance(table, list)
        assert len(table) > 10
        first_row = table[0]
        assert "Type" in first_row
        assert "IAST" in first_row
        assert "Devanagari" in first_row
        assert "Harvard-Kyoto" in first_row


# ---------------------------------------------------------------------------
# 11. Bilingual Explanation and Localization Tests
# ---------------------------------------------------------------------------

class TestBilingualSupport:
    """Verify bilingual (English & Hindi) explanations, outputs, and exact messages."""

    def test_bilingual_analysis_english(self, engine):
        """Default or explicit 'en' returns English rule names and explanations."""
        res = engine.analyze("राम", "ईश्वर", language="en")
        assert res.status == "success"
        assert res.combined == "रामेश्वर"
        assert res.combined_iast == "rāmeśvara"
        assert res.rule_name == "Guṇa Sandhi (गुणसन्धिः)"
        assert res.category == "Svara Sandhi (स्वरसन्धिः)"
        assert res.language == "en"
        assert "vowel" in res.explanation.lower()

    def test_bilingual_analysis_hindi(self, engine):
        """Selecting 'hi' returns authentic Hindi rule names, category, and explanations."""
        res = engine.analyze("राम", "ईश्वर", language="hi")
        assert res.status == "success"
        assert res.combined == "रामेश्वर"
        assert res.combined_iast == "rāmeśvara"
        assert res.rule_name == "गुण सन्धि (गुणसन्धिः)"
        assert res.category == "स्वरसन्धिः (अच्-सन्धिः)"
        assert res.language == "hi"
        assert "गुण" in res.explanation

    def test_localized_method_switching(self, engine):
        """Check that .localized(lang) cleanly toggles between languages."""
        res_orig = engine.analyze("हिम", "आलय", language="en")
        assert res_orig.rule_name == "Dīrgha Sandhi (दीर्घसन्धिः)"

        res_hi = res_orig.localized("hi")
        assert res_hi.rule_name == "दीर्घ सन्धि (दीर्घसन्धिः)"
        assert res_hi.category == "स्वरसन्धिः (अच्-सन्धिः)"
        assert res_hi.language == "hi"
        assert res_hi.combined == "हिमालय"

        res_back_en = res_hi.localized("en")
        assert res_back_en.rule_name == "Dīrgha Sandhi (दीर्घसन्धिः)"
        assert res_back_en.language == "en"

    def test_mode_a_roman_sanskrit_input(self, engine):
        """Mode A: Roman Sanskrit inputs (rāma + īśvara) produce accurate Devanagari combined form."""
        res = engine.analyze("rāma", "īśvara")
        assert res.status == "success"
        assert res.combined == "रामेश्वर"
        assert res.combined_iast == "rāmeśvara"
        assert res.rule_id == "SVAR_02"

    def test_exact_unsupported_error_message_english(self, engine):
        """Verify the exact required error message for unsupported combinations in English."""
        res = engine.analyze("वाक्", "ट", language="en")
        assert res.status == "unsupported"
        expected_msg = (
            "No matching implemented Sandhi rule was found for these inputs. "
            "Please verify the Sanskrit word-parts or consult the Rule Knowledge Base."
        )
        assert res.error_message == expected_msg

    def test_exact_unsupported_error_message_hindi(self, engine):
        """Verify the authentic Hindi error message for unsupported combinations."""
        res = engine.analyze("वाक्", "ट", language="hi")
        assert res.status == "unsupported"
        assert "कोई मान्य पाणिनीय सन्धिनियम नहीं मिला" in res.error_message

    def test_empty_input_bilingual_errors(self, engine):
        """Empty input validation error messages in English and Hindi."""
        res_en = engine.analyze("", "आलय", language="en")
        assert res_en.status == "error"
        assert "cannot be empty" in res_en.error_message

        res_hi = engine.analyze("", "आलय", language="hi")
        assert res_hi.status == "error"
        assert "रिक्त नहीं हो सकता" in res_hi.error_message

