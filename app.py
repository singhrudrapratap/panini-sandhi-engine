# -*- coding: utf-8 -*-
"""
=============================================================================
Pāṇini Vyākaraṇa Sandhi Rule Engine - Web Application (पाणिनीय-सन्धि-तन्त्रम्)
=============================================================================

A modern, responsive Streamlit web application for analyzing Sanskrit Sandhi
according to Pāṇini's Aṣṭādhyāyī and Siddhānta Kaumudī.

Key Features:
- Bilingual Explanation Support: English & हिंदी
- Dual Input Modes: Roman Sanskrit (IAST/HK) & Devanagari Sanskrit
- Live script preview and Roman ambiguity detection
- Large Devanagari result display with Roman IAST
- Working Copy Result & Clear/Reset buttons
- Verified sūtra references and step-by-step phonological derivations
- Interactive Rule Knowledge Base, Grammar Guide & Transliteration Tables
=============================================================================
"""

import os
import sys
import streamlit as st

# Ensure project directory is in sys.path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from transliteration import (
    devanagari_to_iast,
    roman_to_devanagari,
    is_devanagari,
    normalize_sanskrit,
    detect_ambiguities,
    get_transliteration_reference_table
)
from sandhi_engine import (
    PaniniSandhiEngine,
    SandhiResult
)

# ---------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Pāṇini Sandhi Engine | पाणिनीय-सन्धि-तन्त्रम्",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Yatra+One&family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Cinzel:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

    /* Global typography */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans Devanagari', sans-serif;
    }

    /* Sanskrit header hero banner */
    .sanskrit-header {
        text-align: center;
        padding: 1.8rem 1rem 1.4rem 1rem;
        background: linear-gradient(135deg, #78350f 0%, #b45309 45%, #d97706 100%);
        color: #ffffff;
        border-radius: 14px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 16px rgba(180, 83, 9, 0.22);
    }
    .sanskrit-header h1 {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #fef3c7;
        letter-spacing: 0.5px;
    }
    .sanskrit-header h2 {
        font-family: 'Noto Sans Devanagari', 'Yatra One', serif;
        font-size: 1.45rem;
        color: #ffffff;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 0.4rem;
    }
    .sanskrit-header p {
        font-size: 0.95rem;
        color: #fde68a;
        margin: 0;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Result Card */
    .result-card {
        background: #ffffff;
        border: 2px solid #f59e0b;
        border-radius: 14px;
        padding: 1.8rem 1.5rem;
        box-shadow: 0 6px 18px rgba(245, 158, 11, 0.15);
        margin-top: 1rem;
        margin-bottom: 1.2rem;
        text-align: center;
    }
    .combined-title {
        font-family: 'Noto Sans Devanagari', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #b45309;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .combined-iast {
        font-size: 1.35rem;
        font-style: italic;
        color: #4b5563;
        margin-bottom: 0.9rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.3rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.88rem;
        font-weight: 600;
        margin: 0.25rem 0.35rem;
    }
    .badge-sutra {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    .badge-category {
        background-color: #e0e7ff;
        color: #3730a3;
        border: 1px solid #c7d2fe;
    }
    .badge-id {
        background-color: #f3f4f6;
        color: #374151;
        border: 1px solid #e5e7eb;
    }

    /* Step and Explanation Callout */
    .step-box {
        background-color: #f8fafc;
        border-left: 4px solid #d97706;
        padding: 1rem 1.2rem;
        border-radius: 0 10px 10px 0;
        margin-top: 0.6rem;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Ambiguity callout */
    .ambiguity-box {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 0.5rem;
        font-size: 0.88rem;
        color: #92400e;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 2. Engine Singleton Initialization
# ---------------------------------------------------------------------------

@st.cache_resource
def get_engine() -> PaniniSandhiEngine:
    """Load and cache PaniniSandhiEngine singleton from rules.json."""
    rules_path = os.path.join(APP_DIR, "rules.json")
    return PaniniSandhiEngine(rules_path)

engine = get_engine()


# ---------------------------------------------------------------------------
# 3. Session State Management
# ---------------------------------------------------------------------------

if "word1" not in st.session_state:
    st.session_state["word1"] = "हिम"
if "word2" not in st.session_state:
    st.session_state["word2"] = "आलय"
if "input_mode" not in st.session_state:
    st.session_state["input_mode"] = "Devanagari Sanskrit (देवनागरी)"
if "lang_choice" not in st.session_state:
    st.session_state["lang_choice"] = "English"
if "last_analysis" not in st.session_state:
    st.session_state["last_analysis"] = None


def set_preset(w1: str, w2: str, mode: str):
    """Callback to load preset values into session state based on active input mode."""
    if "Roman" in mode:
        st.session_state["word1"] = devanagari_to_iast(w1) if is_devanagari(w1) else w1
        st.session_state["word2"] = devanagari_to_iast(w2) if is_devanagari(w2) else w2
    else:
        st.session_state["word1"] = roman_to_devanagari(w1) if not is_devanagari(w1) else w1
        st.session_state["word2"] = roman_to_devanagari(w2) if not is_devanagari(w2) else w2
    st.session_state["last_analysis"] = None


def clear_all():
    """Callback to reset all inputs and results."""
    st.session_state["word1"] = ""
    st.session_state["word2"] = ""
    st.session_state["last_analysis"] = None


# ---------------------------------------------------------------------------
# 4. Sidebar Controls (Presets, Category Filter, Quick Guide)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🕉️ Pāṇini Sandhi Engine")
    st.caption("Settings, Category Filters & Classical Presets")

    # Category Filter
    filter_options = [
        "All Categories (सर्व-सन्धिः)",
        "Svara Sandhi (स्वरसन्धिः)",
        "Vyañjana Sandhi (व्यञ्जनसन्धिः)",
        "Visarga Sandhi (विसर्गसन्धिः)"
    ]
    selected_filter = st.selectbox(
        "Filter by Sandhi Category:",
        filter_options,
        index=0,
        help="Restrict analysis and knowledge base to specific Sandhi categories."
    )
    cat_filter_str = None if "All" in selected_filter else selected_filter.split(" (")[0]

    st.markdown("---")
    st.markdown("#### 📜 Classical Presets (प्रमाण-उदाहरणानि)")
    st.caption("Select an authoritative classical Sanskrit example:")

    preset_catalog = [
        ("-- Select a Preset --", "", ""),
        # Svara Sandhi
        ("हिम + आलय → हिमालय (Dīrgha 6.1.101)", "हिम", "आलय"),
        ("विद्या + आलय → विद्यालय (Dīrgha 6.1.101)", "विद्या", "आलय"),
        ("कपि + ईश → कपीश (Dīrgha 6.1.101)", "कपि", "ईश"),
        ("भानु + उदय → भानूदय (Dīrgha 6.1.101)", "भानु", "उदय"),
        ("पितृ + ऋणम् → पितॄणम् (Dīrgha 6.1.101)", "पितृ", "ऋणम्"),
        ("नर + ईश → नरेश (Guṇa 6.1.87)", "नर", "ईश"),
        ("देव + इन्द्र → देवेन्द्र (Guṇa 6.1.87)", "देव", "इन्द्र"),
        ("राम + ईश्वर → रामेश्वर (Guṇa 6.1.87)", "राम", "ईश्वर"),
        ("महा + उत्सव → महोत्सव (Guṇa 6.1.87)", "महा", "उत्सव"),
        ("महा + ऋषि → महर्षि (Guṇa 6.1.87)", "महा", "ऋषि"),
        ("तव + ऌकार → तवल्कार (Guṇa 6.1.87)", "तव", "ऌकार"),
        ("सदा + एव → सदैव (Vṛddhi 6.1.88)", "सदा", "एव"),
        ("एक + एक → एकैक (Vṛddhi 6.1.88)", "एक", "एक"),
        ("जल + ओघ → जलौघ (Vṛddhi 6.1.88)", "जल", "ओघ"),
        ("महा + औषध → महौषध (Vṛddhi 6.1.88)", "महा", "औषध"),
        ("इति + आदि → इत्यादि (Yaṇ 6.1.77)", "इति", "आदि"),
        ("प्रति + एक → प्रत्येक (Yaṇ 6.1.77)", "प्रति", "एक"),
        ("सु + आगतम् → स्वागतम् (Yaṇ 6.1.77)", "सु", "आगतम्"),
        ("पितृ + आज्ञा → पित्राज्ञा (Yaṇ 6.1.77)", "पितृ", "आज्ञा"),
        ("ने + अन → नयन (Ayādi 6.1.78)", "ने", "अन"),
        ("पो + अन → पवन (Ayādi 6.1.78)", "पो", "अन"),
        ("नै + अक → नायक (Ayādi 6.1.78)", "नै", "अक"),
        ("पौ + अक → पावक (Ayādi 6.1.78)", "पौ", "अक"),
        ("ते + अपि → तेऽपि (Pūrvarūpa 6.1.109)", "ते", "अपि"),
        ("हरे + अव → हरेऽव (Pūrvarūpa 6.1.109)", "हरे", "अव"),
        ("हरी + एतौ → हरी एतौ (Prakṛtibhāva 1.1.11)", "हरी", "एतौ"),
        # Vyañjana Sandhi
        ("सत् + चित् → सच्चित् (Ścutva 8.4.40)", "सत्", "चित्"),
        ("सत् + जन → सज्जन (Ścutva 8.4.40)", "सत्", "जन"),
        ("रामस् + शेते → रामश्शेते (Ścutva 8.4.40)", "रामस्", "शेते"),
        ("तत् + टीका → तट्टीका (Ṣṭutva 8.4.41)", "तत्", "टीका"),
        ("रामस् + टीकते → रामष्टीकते (Ṣṭutva 8.4.41)", "रामस्", "टीकते"),
        ("वाक् + ईश → वागीश (Jaśtva 8.2.39)", "वाक्", "ईश"),
        ("जगत् + ईश → जगदीश (Jaśtva 8.2.39)", "जगत्", "ईश"),
        ("दिक् + गज → दिग्गज (Jaśtva 8.2.39)", "दिक्", "गज"),
        ("सद् + कार → सत्कार (Cartva 8.4.55)", "सद्", "कार"),
        ("वाक् + मयम् → वाङ्मयम् (Anunāsika 8.4.45)", "वाक्", "मयम्"),
        ("जगत् + नाथ → जगन्नाथ (Anunāsika 8.4.45)", "जगत्", "नाथ"),
        ("हरिम् + वन्दे → हरिं वन्दे (Anusvāra 8.3.23)", "हरिम्", "वन्दे"),
        ("तत् + लय → तल्लय (Torli 8.4.60)", "तत्", "लय"),
        # Visarga Sandhi
        ("रामः + अवदत् → रामोऽवदत् (Utva 6.1.113)", "रामः", "अवदत्"),
        ("कः + अपि → कोऽपि (Utva 6.1.113)", "कः", "अपि"),
        ("रामः + गच्छति → रामो गच्छति (Utva 6.1.114)", "रामः", "गच्छति"),
        ("शिवः + वन्द्यः → शिवो वन्द्यः (Utva 6.1.114)", "शिवः", "वन्द्यः"),
        ("नमः + ते → नमस्ते (Satva 8.3.34)", "नमः", "ते"),
        ("कः + चित् → कश्चित् (Satva 8.3.34)", "कः", "चित्"),
        ("धनुः + टङ्कार → धनुष्टङ्कार (Satva 8.3.34)", "धनुः", "टङ्कार"),
        ("हरिः + आगच्छति → हरिरागच्छति (Rutva 8.2.66)", "हरिः", "आगच्छति"),
        ("मुनिः + गच्छति → मुनिर्गच्छति (Rutva 8.2.66)", "मुनिः", "गच्छति"),
        ("बालाः + नमन्ति → बाला नमन्ति (Lopa 8.3.17)", "बालाः", "नमन्ति"),
        ("रामः + आगच्छति → राम आगच्छति (Lopa 8.3.17)", "रामः", "आगच्छति"),
        ("सः + गच्छति → स गच्छति (Lopa 6.1.132)", "सः", "गच्छति")
    ]

    selected_preset_tuple = st.selectbox(
        "Choose Preset:",
        preset_catalog,
        format_func=lambda x: x[0]
    )

    if selected_preset_tuple[0] != "-- Select a Preset --":
        if st.button("📥 Load Preset into Analyzer", use_container_width=True):
            set_preset(selected_preset_tuple[1], selected_preset_tuple[2], st.session_state["input_mode"])
            st.rerun()

    st.markdown("---")
    st.markdown("#### 💡 Quick Viva Demo Tip")
    st.info(
        "Demonstrate the difference between **Ścutva** (voicing in `सत् + जन → सज्जन`) "
        "and **Pūrvarūpa vs Ayādi** (`ने + अन → नयन` vs `ते + अपि → तेऽपि`)."
    )


# ---------------------------------------------------------------------------
# 5. Header & Controls Bar
# ---------------------------------------------------------------------------

st.markdown("""
<div class="sanskrit-header">
    <h1>Pāṇini Vyākaraṇa Sandhi Rule Engine</h1>
    <h2>पाणिनीय-व्याकरण-सन्धिनियम-तन्त्रम्</h2>
    <p>An Advanced Computational Sanskrit Grammar Analyzer & Educational Engine Based on Pāṇini's Aṣṭādhyāyī</p>
</div>
""", unsafe_allow_html=True)

# Top Controls Bar: Bilingual Explanation Selector & Input Mode Selector
ctrl_col1, ctrl_col2 = st.columns([1, 1])

with ctrl_col1:
    input_mode = st.radio(
        "⌨️ Input Script Mode (प्रविष्टि-माध्यमः):",
        ["Mode A: Roman Sanskrit (IAST / HK)", "Mode B: Devanagari Sanskrit (देवनागरी)"],
        index=0 if "Roman" in st.session_state["input_mode"] else 1,
        horizontal=True,
        help="Select whether you want to type Sanskrit word-parts in Roman transliteration (e.g. rāma + īśvara) or Devanagari (राम + ईश्वर)."
    )
    st.session_state["input_mode"] = input_mode

with ctrl_col2:
    lang_choice = st.radio(
        "🌐 Explanation Language (व्याख्या-भाषा):",
        ["English", "हिंदी (Hindi)"],
        index=0 if st.session_state["lang_choice"] == "English" else 1,
        horizontal=True,
        help="Switch explanation, step derivations, and UI labels between English and Hindi."
    )
    is_hindi = "हिंदी" in lang_choice
    lang_code = "hi" if is_hindi else "en"
    st.session_state["lang_choice"] = "हिंदी" if is_hindi else "English"


# ---------------------------------------------------------------------------
# 6. Tabbed Interface
# ---------------------------------------------------------------------------

tab_analyzer, tab_browser, tab_guide, tab_translit = st.tabs([
    "🔍 Sandhi Analyzer (सन्धि-विश्लेषणम्)",
    "📚 Rule Knowledge Base (सन्धिनियम-सङ्ग्रहः)",
    "📖 Pāṇini Grammar Guide (पाणिनीय-परिचयः)",
    "🔤 Transliteration Reference (लिप्यन्तरण-तालिका)"
])


# ===========================================================================
# TAB 1: SANDHI ANALYZER
# ===========================================================================

with tab_analyzer:
    st.markdown(
        "### 📝 Sanskrit Word Parts Entry (पद-प्रविष्टिः)" if not is_hindi
        else "### 📝 संस्कृत पद-प्रविष्टि (पूर्वपदम् एवं उत्तरपदम्)"
    )

    if "Roman" in input_mode:
        st.caption(
            "🔤 **Roman Sanskrit Mode Active:** Enter Sanskrit words using academic IAST (e.g. `rāma`, `īśvara`, `hima`, `ālaya`, `sat`, `cit`) or Harvard-Kyoto. "
            "*(Note: This is Sanskrit in Roman script, not English translation).* "
        )
    else:
        st.caption(
            "🕉️ **देवनागरी माध्यम सक्रिय:** संस्कृत पदों को सीधे देवनागरी में लिखें (उदा. `राम`, `ईश्वर`, `हिम`, `आलय`, `सत्`, `चित्`, `रामः`, `अवदत्`)।"
        )

    in_col1, in_col2 = st.columns(2)

    with in_col1:
        label_w1 = "First Word (पूर्वपदम् / Pūrva-pada):" if not is_hindi else "प्रथम पद (पूर्वपदम्):"
        placeholder_w1 = "e.g., rāma / hima / sat / rāmaḥ" if "Roman" in input_mode else "उदा. राम / हिम / सत् / रामः"
        val_w1 = st.text_input(
            label_w1,
            value=st.session_state["word1"],
            key="text_input_w1",
            placeholder=placeholder_w1
        )
        # Normalized preview
        if val_w1.strip():
            norm_w1_dev = val_w1.strip() if is_devanagari(val_w1.strip()) else roman_to_devanagari(val_w1.strip())
            norm_w1_iast = devanagari_to_iast(norm_w1_dev)
            st.markdown(f"**Preview:** देवनागरी: `{norm_w1_dev}` &nbsp;|&nbsp; IAST: *{norm_w1_iast}*")
            # Ambiguity notice
            amb_w1 = detect_ambiguities(val_w1)
            for aw in amb_w1:
                issue_text = aw["issue_hi"] if is_hindi else aw["issue_en"]
                sugg_text = aw["suggestion_hi"] if is_hindi else aw["suggestion_en"]
                st.markdown(f"""
                <div class="ambiguity-box">
                    ⚠️ <strong>{aw['pattern']}:</strong> {issue_text} <em>({sugg_text})</em>
                </div>
                """, unsafe_allow_html=True)

    with in_col2:
        label_w2 = "Second Word (उत्तरपदम् / Uttara-pada):" if not is_hindi else "द्वितीय पद (उत्तरपदम्):"
        placeholder_w2 = "e.g., īśvara / ālaya / cit / gacchati" if "Roman" in input_mode else "उदा. ईश्वर / आलय / चित् / गच्छति"
        val_w2 = st.text_input(
            label_w2,
            value=st.session_state["word2"],
            key="text_input_w2",
            placeholder=placeholder_w2
        )
        # Normalized preview
        if val_w2.strip():
            norm_w2_dev = val_w2.strip() if is_devanagari(val_w2.strip()) else roman_to_devanagari(val_w2.strip())
            norm_w2_iast = devanagari_to_iast(norm_w2_dev)
            st.markdown(f"**Preview:** देवनागरी: `{norm_w2_dev}` &nbsp;|&nbsp; IAST: *{norm_w2_iast}*")
            amb_w2 = detect_ambiguities(val_w2)
            for aw in amb_w2:
                issue_text = aw["issue_hi"] if is_hindi else aw["issue_en"]
                sugg_text = aw["suggestion_hi"] if is_hindi else aw["suggestion_en"]
                st.markdown(f"""
                <div class="ambiguity-box">
                    ⚠️ <strong>{aw['pattern']}:</strong> {issue_text} <em>({sugg_text})</em>
                </div>
                """, unsafe_allow_html=True)

    # Action Buttons: Prominent Analyze & Reset
    btn_col1, btn_col2, btn_col3 = st.columns([2.5, 1.5, 3])

    with btn_col1:
        analyze_btn_label = "⚡ Analyze Sandhi (सन्धिं कुरु)" if not is_hindi else "⚡ सन्धि-विश्लेषण करें (सन्धिं कुरु)"
        analyze_clicked = st.button(analyze_btn_label, type="primary", use_container_width=True)

    with btn_col2:
        clear_btn_label = "🔄 Reset / Clear (पुनः कुरु)" if not is_hindi else "🔄 पुनः कुरु (साफ़ करें)"
        clear_clicked = st.button(clear_btn_label, use_container_width=True)
        if clear_clicked:
            clear_all()
            st.rerun()

    # Trigger analysis
    if analyze_clicked:
        st.session_state["word1"] = val_w1
        st.session_state["word2"] = val_w2
        with st.spinner("Analyzing Sandhi with Pāṇini's Aṣṭādhyāyī rules..." if not is_hindi else "पाणिनीय व्याकरण नियमों से विश्लेषण किया जा रहा है..."):
            res = engine.analyze(
                val_w1,
                val_w2,
                category_filter=cat_filter_str,
                language=lang_code
            )
            st.session_state["last_analysis"] = res

    # Display Analysis Result
    if st.session_state["last_analysis"]:
        res: SandhiResult = st.session_state["last_analysis"]

        # Ensure correct localization view
        res = res.localized(lang_code)

        st.markdown("---")

        if res.status == "success":
            st.markdown(
                "### 🎯 Sandhi Result (सन्धि-फलम्)" if not is_hindi
                else "### 🎯 सन्धि-फलम् (विश्लेषण परिणाम)"
            )

            # Prominent Sanskrit Result Card
            st.markdown(f"""
            <div class="result-card">
                <div style="font-size: 1.15rem; color: #4b5563; margin-bottom: 0.4rem;">
                    <strong>{res.word1}</strong> ({res.word1_iast}) &nbsp;+&nbsp; <strong>{res.word2}</strong> ({res.word2_iast}) &nbsp;=
                </div>
                <div class="combined-title">{res.combined}</div>
                <div class="combined-iast">{res.combined_iast}</div>
                <div style="margin-top: 0.5rem;">
                    <span class="badge-pill badge-id">ID: {res.rule_id}</span>
                    <span class="badge-pill badge-category">{res.category}</span>
                    <span class="badge-pill badge-sutra">📖 {res.sutra} ({res.reference})</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Copy Result Toolbar
            copy_col1, copy_col2 = st.columns([1, 1])
            with copy_col1:
                st.caption("📋 One-click copy Sanskrit result:" if not is_hindi else "📋 परिणाम कॉपी करें:")
                st.code(res.combined, language=None)
            with copy_col2:
                st.caption("📋 Copy Roman IAST result:" if not is_hindi else "📋 रोमन (IAST) रूप कॉपी करें:")
                st.code(res.combined_iast, language=None)

            # Detailed Explanation & Step Derivations
            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.markdown(
                    "#### 🔬 Phonological Boundary Analysis" if not is_hindi
                    else "#### 🔬 वर्ण-विश्लेषण एवं सन्धि-प्रक्रिया"
                )
                st.markdown(f"""
                - **Pūrva-pada (पूर्वपदम्):** `{res.word1}` (*{res.word1_iast}*)
                - **Uttara-pada (उत्तरपदम्):** `{res.word2}` (*{res.word2_iast}*)
                - **Boundary Operation:** `{res.transformation_detail}`
                """)
                st.markdown(f"""
                <div class="step-box">
                    <strong>{'Step-by-Step Derivation:' if not is_hindi else 'क्रमशः रूप-सिद्धि:'}</strong><br>
                    {res.boundary_breakdown}
                </div>
                """, unsafe_allow_html=True)

            with detail_col2:
                st.markdown(
                    "#### 📜 Pāṇini Sūtra & Grammar Commentary" if not is_hindi
                    else "#### 📜 पाणिनीय सूत्र एवं कौमुदी-व्याख्या"
                )
                st.markdown(f"""
                - **Rule Name:** **{res.rule_name}**
                - **Sūtra Reference:** `{res.sutra}` ({res.reference})
                - **Category:** `{res.category}`
                """)
                st.markdown(f"""
                <div class="step-box">
                    <strong>{'Grammatical Explanation:' if not is_hindi else 'व्याकरण-व्याख्या:'}</strong><br>
                    {res.explanation}
                </div>
                """, unsafe_allow_html=True)

        elif res.status == "no_sandhi":
            st.info(
                f"ℹ️ **Hiatus / No Sandhi Merger (प्रकृतिभावः):**\n\n{res.explanation}\n\n**Resulting Juncture:** `{res.combined}`"
                if not is_hindi else
                f"ℹ️ **प्रकृतिभाव / कोई सन्धि-विकार नहीं:**\n\n{res.explanation}\n\n**पद-स्वरूप:** `{res.combined}`"
            )
            st.code(res.combined, language=None)

        elif res.status == "error":
            st.error(f"⚠️ **Input Error:** {res.error_message}")

        elif res.status == "unsupported":
            st.warning(f"⚠️ **Notice:** {res.error_message}")
            if res.boundary_breakdown:
                st.caption(f"Detected Boundary: {res.boundary_breakdown}")


# ===========================================================================
# TAB 2: RULE KNOWLEDGE BASE
# ===========================================================================

with tab_browser:
    st.markdown(
        "### 📚 Pāṇini Sandhi Knowledge Base (सन्धिनियम-सङ्ग्रहः)" if not is_hindi
        else "### 📚 पाणिनीय सन्धिनियम-सङ्ग्रह (ज्ञान-कोश)"
    )
    st.write(
        "Explore all 19 verified Sandhi rules implemented in the engine, categorized by Svara, Vyañjana, and Visarga Sandhi with classical citations."
        if not is_hindi else
        "इंजन में कार्यान्वित सभी १९ प्रामाणिक सन्धिनियमों को अष्टाध्यायी सूत्रों, अर्थ एवं शास्त्रीय उदाहरणों सहित देखें:"
    )

    rules_list = engine.get_rules_by_category(cat_filter_str)
    st.caption(f"Showing {len(rules_list)} rules in category: '{selected_filter}'")

    for r in rules_list:
        display_name = r.get("rule_name_hi" if is_hindi else "rule_name_en", r["rule_name"])
        display_cat = r.get("category_hi" if is_hindi else "category_en", r["category"])
        display_desc = r.get("description_hi" if is_hindi else "description_en", r["description"])
        display_exp = r.get("explanation_hi" if is_hindi else "explanation_en", r["explanation"])
        display_trans = r.get("transformation_hi" if is_hindi else "transformation_en", r["transformation"])

        with st.expander(f"📌 [{r['rule_id']}] {display_name} — {r['sutra']} ({r['reference']})"):
            st.markdown(f"**Category:** `{display_cat}` | **Pratyāhāra / Scope:** `{r.get('pratyahara', 'General')}`")
            st.markdown(f"**Sūtra Meaning:** {display_desc}")
            st.markdown(f"**Transformation Rule:** `{display_trans}`")
            st.markdown(f"**Grammatical Commentary:** {display_exp}")

            st.markdown("##### Verified Classical Examples:")
            ex_cols = st.columns(min(3, max(1, len(r.get("examples", [])))))
            for idx, ex in enumerate(r.get("examples", [])):
                target_col = ex_cols[idx % len(ex_cols)]
                with target_col:
                    st.markdown(f"""
                    - **{ex['word1']} + {ex['word2']} = {ex['combined']}**
                      - *IAST:* {ex.get('word1_iast', '')} + {ex.get('word2_iast', '')} = {ex.get('combined_iast', '')}
                      - *Meaning:* {ex.get('meaning_hi' if is_hindi else 'meaning', ex.get('meaning', ''))}
                      - *Boundary:* `{ex.get('boundary', '')}`
                    """)


# ===========================================================================
# TAB 3: PĀṆINI GRAMMAR GUIDE
# ===========================================================================

with tab_guide:
    if not is_hindi:
        st.markdown("### 📖 Pāṇini Grammar Guide & Architectural Reference")
        st.markdown("""
        #### 1. What is Sandhi (सन्धिः)?
        In Sanskrit linguistics, **Sandhi** (*"euphonic combination"*) refers to the phonological modifications that occur at word or morpheme boundaries.
        Pāṇini defines the locus of Sandhi in *Aṣṭādhyāyī* 1.4.109:
        > **परः संनिकर्षः संहिता (१.४.१०९)** — *"The closest phonetic proximity between sounds is termed Saṁhitā."*

        #### 2. Three Major Classes of Sandhi
        1. **Svara Sandhi (स्वरसन्धिः / अच्-सन्धिः - Vowel Sandhi):**
           Modifications occurring when a vowel-ending word meets a vowel-beginning word.
           - *Dīrgha Sandhi* (6.1.101): अकः सवर्णे दीर्घः
           - *Guṇa Sandhi* (6.1.87): आद्गुणः
           - *Vṛddhi Sandhi* (6.1.88): वृद्धिरेचि
           - *Yaṇ Sandhi* (6.1.77): इको यणचि
           - *Ayādi Sandhi* (6.1.78): एचोऽयवायावः
           - *Pūrvarūpa Sandhi* (6.1.109): एङः पदान्तादति
           - *Prakṛtibhāva Sandhi* (1.1.11, 6.1.125): ईदूदेद्द्विवचनं प्रगृह्यम्

        2. **Vyañjana Sandhi (व्यञ्जनसन्धिः / हल्-सन्धिः - Consonant Sandhi):**
           Modifications when a consonant encounters another consonant or vowel.
           - *Ścutva Sandhi* (8.4.40): स्तोः श्चुना श्चुः (Palatal assimilation)
           - *Ṣṭutva Sandhi* (8.4.41): ष्टुना ष्टुः (Retroflex assimilation)
           - *Jaśtva Sandhi* (8.2.39): झलां जशोऽन्ते (Voicing / 3rd class consonant substitution)
           - *Cartva Sandhi* (8.4.55): खरि च (Devoicing / 1st class consonant substitution)
           - *Anunāsika Sandhi* (8.4.45): यरोऽनुनासिकेऽनुनासिको वा (Nasal assimilation)
           - *Anusvāra Sandhi* (8.3.23): मोऽनुस्वारः (Final 'm' to anusvāra before consonant)
           - *Torli Sandhi* (8.4.60): तोर्लि (Dental stop before 'l' assimilates)

        3. **Visarga Sandhi (विसर्गसन्धिः):**
           Transformations of word-final visarga (`ः`) before vowels or consonants.
           - *Utva Sandhi* (6.1.113): अतो रोरप्लुतादप्लुते (Visarga to 'o' before short a)
           - *Utva Sandhi* (6.1.114): हशि च (Visarga to 'o' before voiced consonants)
           - *Satva / Sibilant Sandhi* (8.3.34): विसर्जनीयस्य सः (Visarga to sibilant)
           - *Rutva Sandhi* (8.2.66): ससजुषो रुः (Visarga to 'r' after non-a vowels)
           - *Visarga Lopa Sandhi* (8.3.17, 8.3.19, 6.1.132): Visarga drops

        #### 3. Why a Rule Engine Over Machine Learning?
        Pāṇini's Vyākaraṇa is an axiomatic, deterministic generative grammar. A transparent rule engine guarantees **100% explainability**, provides exact sūtra citations, and prevents hallucinated output on ancient languages.
        """)
    else:
        st.markdown("### 📖 पाणिनीय व्याकरण एवं सन्धिनियम परिचय")
        st.markdown("""
        #### १. सन्धि किसे कहते हैं?
        संस्कृत व्याकरण में दो समीपवर्ती वर्णों के परस्पर मेल से होने वाले विकार (ध्वनि-परिवर्तन) को **सन्धि** कहते हैं।
        महर्षि पाणिनि ने अष्टाध्यायी में सन्धि (संहिता) की परिभाषा दी है:
        > **परः संनिकर्षः संहिता (१.४.१०९)** — *वर्णों की अत्यधिक सन्निकटता (निकटता) को संहिता कहते हैं।*

        #### २. सन्धि के तीन मुख्य भेद:
        १. **स्वरसन्धिः (अच्-सन्धिः):**
           दो स्वरों के परस्पर मिलने पर होने वाला विकार।
           - *दीर्घ सन्धि* (६.१.१०१): अकः सवर्णे दीर्घः
           - *गुण सन्धि* (६.१.८७): आद्गुणः
           - *वृद्धि सन्धि* (६.१.८८): वृद्धिरेचि
           - *यण् सन्धि* (६.१.७७): इको यणचि
           - *अयादि सन्धि* (६.१.७८): एचोऽयवायावः
           - *पूर्वरूप सन्धि* (६.१.१०९): एङः पदान्तादति
           - *प्रकृतिभाव सन्धि* (१.१.११): ईदूदेद्द्विवचनं प्रगृह्यम्

        २. **व्यञ्जनसन्धिः (हल्-सन्धिः):**
           व्यञ्जन के साथ व्यञ्जन अथवा स्वर के मिलने पर होने वाला परिवर्तन।
           - *श्चुत्व सन्धि* (८.४.४०): स्तोः श्चुना श्चुः (तालव्य परिवर्तन)
           - *ष्टुत्व सन्धि* (८.४.४१): ष्टुना ष्टुः (मूर्धन्य परिवर्तन)
           - *जश्त्व सन्धि* (८.२.३९): झलां जशोऽन्ते (वर्ग का तृतीय वर्ण)
           - *चर्त्व सन्धि* (८.४.५५): खरि च (वर्ग का प्रथम अघोष वर्ण)
           - *अनुनासिक सन्धि* (८.४.४५): यरोऽनुनासिकेऽनुनासिको वा (पञ्चम वर्ण)
           - *अनुस्वार सन्धि* (८.३.२३): मोऽनुस्वारः (पदान्त 'म्' का अनुस्वार)
           - *तोर्लि सन्धि* (८.४.६०): तोर्लि (त-वर्ग का 'ल्' में परिवर्तन)

        ३. **विसर्गसन्धिः:**
           विसर्ग (ः) के साथ स्वर अथवा व्यञ्जन के मिलने पर होने वाला परिवर्तन।
           - *उत्व सन्धि* (६.१.११३): अतो रोरप्लुतादप्लुते (ह्रस्व 'अ' परे होने पर)
           - *उत्व सन्धि* (६.१.११४): हशि च (घोष व्यञ्जन परे होने पर)
           - *सत्व सन्धि* (८.३.३४): विसर्जनीयस्य सः (विसर्ग का श्/ष्/स्)
           - *रुत्व सन्धि* (८.२.६६): ससजुषो रुः (विसर्ग का 'र्')
           - *विसर्गलोप सन्धि* (८.३.१७): विसर्ग का लोप होना
        """)


# ===========================================================================
# TAB 4: TRANSLITERATION REFERENCE
# ===========================================================================

with tab_translit:
    st.markdown(
        "### 🔤 Supported Transliteration Schemes (IAST & Harvard-Kyoto)" if not is_hindi
        else "### 🔤 संस्कृत लिप्यन्तरण तालिका (IAST एवं हार्वर्ड-क्योटो)"
    )
    st.write(
        "The engine accurately converts Roman Sanskrit transliteration into Devanagari Unicode. Below is the complete mapping table:"
        if not is_hindi else
        "इंजन रोमन संस्कृत लिप्यन्तरण को शुद्ध देवनागरी में परिवर्तित करता है। नीचे वर्णमाला का सम्पूर्ण मानचित्रण दिया गया है:"
    )

    translit_data = get_transliteration_reference_table()
    st.dataframe(translit_data, use_container_width=True, hide_index=True)

    st.markdown("#### 💡 Transliteration Conventions & Ambiguity Notes:")
    st.markdown("""
    - **Academic IAST:** Uses macron for long vowels (`ā, ī, ū`), underdot for retroflexes (`ṭ, ḍ, ṇ, ṣ`), and acute/overdot for palatal sibilant (`ś`).
    - **Harvard-Kyoto (HK):** Uses capital letters for long vowels (`A, I, U, R, RR`), capital consonants for retroflexes (`T, D, N, S`), and `z` for palatal `ś`.
    - **Ambiguity Prevention:** Avoid plain English approximations like `sh` (which can be `ś`/श or `ṣ`/ष). Use `ś` for श and `ṣ` for ष.
    """)
