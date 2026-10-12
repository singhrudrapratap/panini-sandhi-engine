# 🕉️ Pāṇini Vyākaraṇa Sandhi Rule Engine
### *पाणिनीय-व्याकरण-सन्धिनियम-तन्त्रम्*

An advanced, rule-based computational Sanskrit grammar analyzer and educational platform based on **Pāṇini’s Aṣṭādhyāyī** and Bhaṭṭoji Dīkṣita’s **Siddhānta Kaumudī**.

Built for college final-year projects, Sanskrit computational linguistics demonstrations, and beginner-to-advanced scholars of Vyākaraṇa.

---

## 📌 1. Project Overview

In Sanskrit grammar, **Sandhi** (*"euphonic combination"*) is the phonological modification occurring at morpheme and word boundaries:

$$\text{संहितैकपदे नित्या नित्या धातूपसर्गयोः । नित्या समासे वाक्ये तु सा विवक्षामपेक्षते ॥}$$

Pāṇini defines Sandhi (*Saṁhitā*) in sūtra 1.4.109:
> **परः संनिकर्षः संहिता (१.४.१०९)** — *"The closest phonetic proximity between sounds is termed Saṁhitā."*

This project implements a **pure, transparent, rule-driven computational engine** in Python that accepts two Sanskrit word parts (पूर्वपदम् / Pūrva-pada and उत्तरपदम् / Uttara-pada), determines the applicable Pāṇinian rule, computes the exact combined form, and generates step-by-step phonological derivations with classical sūtra citations.

---

## ✨ 2. Key Features

- **🏛️ 19 Authoritative Pāṇinian Rules Implemented**:
  - **Svara Sandhi (स्वरसन्धिः / Vowel Sandhi)**: Dīrgha (6.1.101), Guṇa (6.1.87), Vṛddhi (6.1.88), Yaṇ (6.1.77), Ayādi (6.1.78), Pūrvarūpa (6.1.109), and Prakṛtibhāva (1.1.11, 6.1.125).
  - **Vyañjana Sandhi (व्यञ्जनसन्धिः / Consonant Sandhi)**: Ścutva (8.4.40), Ṣṭutva (8.4.41), Jaśtva (8.2.39), Cartva (8.4.55), Anunāsika (8.4.45), Anusvāra (8.3.23), and Torli (8.4.60).
  - **Visarga Sandhi (विसर्गसन्धिः)**: Utva before short a (6.1.113), Utva before voiced consonants (6.1.114), Satva / Sibilant assimilation (8.3.34), Rutva (8.2.66), and Visarga Lopa (8.3.17, 8.3.19, 6.1.132).

- **🔤 Bilingual Input Modes**:
  - **Mode A: Roman Sanskrit (IAST / Harvard-Kyoto)**: e.g. `rāma` + `īśvara` ➔ `रामेश्वर`, or `sat` + `cit` ➔ `सच्चित्`.
  - **Mode B: Devanagari Sanskrit**: e.g. `राम` + `ईश्वर` ➔ `रामेश्वर`, or `सत्` + `चित्` ➔ `सच्चित्`.
  - Live cross-script preview showing the normalized input and equivalent script in real time.

- **🔤 Standalone Transliteration Module (`transliteration.py`)**:
  - Independent bidirectional transliteration engine between Roman (IAST, Harvard-Kyoto) and Devanagari.
  - Handles long/short vowels, aspirated consonants (`kh`, `gh`, `th`, `dh`), retroflexes (`ṭ`, `ḍ`, `ṇ`, `ṣ`), anusvāra (`ṁ`), visarga (`ḥ`), avagraha (`'`), and conjuncts.
  - **Ambiguity Detection**: Non-silent warnings for ambiguous Roman ASCII inputs (e.g. plain `sh` vs `ś`/`ṣ`, `ch` vs `c`, or missing long macrons `a` vs `ā`).
  - Searchable Transliteration Reference Table built into the UI.

- **🌐 Hindi & English Bilingual Explanations**:
  - Visible language toggle (**English** / **हिंदी**).
  - **English Mode**: Grammatical explanations, step-by-step phoneme breakdowns, and category names in English.
  - **Hindi Mode**: Authentic Hindi translations of rule names (e.g. *गुण सन्धि (गुणसन्धिः)*), categories (*स्वरसन्धिः (अच्-सन्धिः)*), and classical derivations.
  - **Strict Sanskrit Preservation**: The resulting Sanskrit word is always presented in prominent Devanagari script, regardless of the explanation language selected.

- **🔬 Step-by-Step Phonological Breakdown**:
  - Highlights the Pūrva ending sound (अन्त्यवर्णः) and Uttara initial sound (आदिवर्णः).
  - Explains the exact phonetic transition (विकारः / सन्ध्यक्षरम्).

- **🛡️ Strict Linguistic Rigor & Safe Fallback**:
  - Zero hallucinations or false positives: No artificial machine learning predictions.
  - Exact verified fallback for unsupported combinations:
    > *"No matching implemented Sandhi rule was found for these inputs. Please verify the Sanskrit word-parts or consult the Rule Knowledge Base."*
  - Safe Unicode normalization (NFC) preserving halanta (्), mātrās, anusvāra (ं), visarga (ः), and avagraha (ऽ).

- **🎨 Modern Scholarly Web Interface**:
  - Built with Streamlit featuring a refined Sanskrit scholarly aesthetic.
  - Large Devanagari result typography (3.2rem) with secondary IAST transliteration.
  - One-click **Copy Result** snippet and **Reset / Clear** controls.
  - Tabbed organization: Sandhi Analyzer, Rule Knowledge Base, Pāṇini Grammar Guide, and Transliteration Guide.

- **🧪 100% Automated Test Coverage**:
  - **167 automated pytest test assertions** verifying every rule, edge cases, whitespace, transliteration, ambiguities, and bilingual outputs.

---

## 🛠️ 3. Technology Stack

- **Language:** Python 3.10+ (tested on Python 3.11)
- **Web UI:** Streamlit (`>=1.30.0`)
- **Transliteration:** Dedicated modular engine (`transliteration.py`)
- **Rule Storage:** Declarative JSON (`rules.json`)
- **Test Automation:** Pytest (`>=7.4.0`)
- **Text Standards:** Unicode 15.0 NFC Normalization, standard IAST / Harvard-Kyoto transliteration

---

## 📁 4. Project Structure

```
panini-sandhi-engine/
├── app.py                 # Streamlit web application & bilingual user interface
├── sandhi_engine.py       # Core Sanskrit phonology & Pāṇinian rule engine
├── transliteration.py     # Standalone bidirectional transliteration & ambiguity detector
├── rules.json             # Canonical rule definitions with bilingual (EN/HI) metadata
├── requirements.txt       # Python dependencies (streamlit, pytest)
├── README.md              # Complete technical documentation & setup guide
├── .gitignore             # Git ignore configuration
└── tests/
    └── test_sandhi.py     # Comprehensive automated test suite (167 passing tests)
```

---

## 🚀 5. Installation & Setup (Windows Guide)

### Prerequisites
Make sure Python 3.10 or higher is installed on your Windows machine:

```powershell
python --version
```

### Step 1: Open PowerShell and Navigate to the Project
```powershell
cd "c:\Users\ANGEL COMPUTERS\Desktop\tydspor\panini-sandhi-engine"
```

### Step 2: Create a Python Virtual Environment
Creating a virtual environment ensures dependencies remain isolated and clean:

```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -RemoteSigned -Scope CurrentUser` once).*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 💻 6. How to Run the Application

With your virtual environment activated, launch the Streamlit web interface:

```powershell
streamlit run app.py
```

Streamlit will open the interactive dashboard in your default browser at:
```
http://localhost:8501
```

---

## 🧪 7. How to Run Automated Tests

The project includes an automated Pytest test suite covering all 19 rules, 70+ classical examples, edge cases, bidirectional transliteration, and bilingual localization:

```powershell
pytest tests/test_sandhi.py -v
```

Expected result:
```
============================= 167 passed in 0.31s =============================
```

---

## 📚 8. Overview of Implemented Pāṇinian Rules

| Rule ID | Rule Name (EN / HI) | Sūtra | Reference | Input Pattern | Resulting Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SVAR_01** | Dīrgha Sandhi / दीर्घसन्धिः | अकः सवर्णे दीर्घः | 6.1.101 | a/i/u/ṛ + savarṇa | हिम + आलय = **हिमालय** |
| **SVAR_02** | Guṇa Sandhi / गुणसन्धिः | आद्गुणः | 6.1.87 | a/ā + i/u/ṛ/ḷ | राम + ईश्वर = **रामेश्वर** |
| **SVAR_03** | Vṛddhi Sandhi / वृद्धिसन्धिः | वृद्धिरेचि | 6.1.88 | a/ā + e/ai/o/au | सदा + एव = **सदैव** |
| **SVAR_04** | Yaṇ Sandhi / यण्सन्धिः | इको यणचि | 6.1.77 | i/u/ṛ/ḷ + dissimilar | इति + आदि = **इत्यादि** |
| **SVAR_05** | Ayādi Sandhi / अयादिसन्धिः | एचोऽयवायावः | 6.1.78 | e/o/ai/au + vowel | ने + अन = **नयन** |
| **SVAR_06** | Pūrvarūpa Sandhi / पूर्वरूपसन्धिः | एङः पदान्तादति | 6.1.109 | e/o (padānta) + short a | ते + अपि = **तेऽपि** |
| **SVAR_07** | Prakṛtibhāva Sandhi / प्रकृतिभावः | ईदूदेद्द्विवचनं प्रगृह्यम् | 1.1.11 | dual ī/ū/e + vowel | हरी + एतौ = **हरी एतौ** |
| **VYAN_01** | Ścutva Sandhi / श्चुत्वसन्धिः | स्तोः श्चुना श्चुः | 8.4.40 | dental + palatal | सत् + चित् = **सच्चित्** |
| **VYAN_02** | Ṣṭutva Sandhi / ष्टुत्वसन्धिः | ष्टुना ष्टुः | 8.4.41 | dental + retroflex | तत् + टीका = **तट्टीका** |
| **VYAN_03** | Jaśtva Sandhi / जश्त्वसन्धिः | झलां जशोऽन्ते | 8.2.39 | stop + voiced/vowel | वाक् + ईश = **वागीश** |
| **VYAN_04** | Cartva Sandhi / चर्त्वसन्धिः | खरि च | 8.4.55 | voiced stop + voiceless | सद् + कार = **सत्कार** |
| **VYAN_05** | Anunāsika Sandhi / अनुनासिकसन्धिः | यरोऽनुनासिकेऽनुनासिको वा | 8.4.45 | stop + nasal | जगत् + नाथ = **जगन्नाथ** |
| **VYAN_06** | Anusvāra Sandhi / अनुस्वारसन्धिः | मोऽनुस्वारः | 8.3.23 | padānta m + cons | हरिम् + वन्दे = **हरिं वन्दे** |
| **VYAN_07** | Torli Sandhi / तोर्लिसन्धिः | तोर्लि | 8.4.60 | dental stop + l | तत् + लय = **तल्लय** |
| **VIS_01** | Utva Sandhi (a) / उत्वसन्धिः | अतो रोरप्लुतादप्लुते | 6.1.113 | aḥ + short a | रामः + अवदत् = **रामोऽवदत्** |
| **VIS_02** | Utva Sandhi (haś) / उत्वसन्धिः | हशि च | 6.1.114 | aḥ + voiced cons | रामः + गच्छति = **रामो गच्छति** |
| **VIS_03** | Satva Sandhi / सत्वसन्धिः | विसर्जनीयस्य सः | 8.3.34 | ḥ + voiceless stop | नमः + ते = **नमस्ते** |
| **VIS_04** | Rutva Sandhi / रुत्वसन्धिः | ससजुषो रुः | 8.2.66 | non-a/ā visarga + voiced | हरिः + आगच्छति = **हरिरागच्छति** |
| **VIS_05** | Visarga Lopa / विसर्गलोपः | भोभगोअघोअपूर्वस्य योऽशि | 8.3.17 | āḥ/saḥ/aḥ + voiced/vowel | बालाः + नमन्ति = **बाला नमन्ति** |

---

## 💡 9. Demonstration Queries for College Presentation

You can demonstrate these live during your project presentation:

1. **Mode A (Roman Sanskrit)**:
   - Enter `rāma` and `īśvara` ➔ Combines into **रामेश्वर** (*Guṇa Sandhi 6.1.87*).
   - Enter `sat` and `cit` ➔ Combines into **सच्चित्** (*Ścutva Sandhi 8.4.40*).
   - Enter `namaḥ` and `te` ➔ Combines into **नमस्ते** (*Satva Sandhi 8.3.34*).
2. **Mode B (Devanagari Sanskrit)**:
   - Enter `हिम` and `आलय` ➔ Combines into **हिमालय** (*Dīrgha Sandhi 6.1.101*).
   - Enter `महा` and `ऋषि` ➔ Combines into **महर्षि** (*Guṇa Sandhi with 1.1.51 Uraṇ raparaḥ*).
   - Enter `सु` and `आगतम्` ➔ Combines into **स्वागतम्** (*Yaṇ Sandhi 6.1.77*).
3. **Bilingual Language Toggle**:
   - Toggle language selector between **English** and **हिंदी**.
   - Notice the explanation changes dynamically while the Sanskrit result remains authentic Devanagari.
4. **Ambiguity Feedback**:
   - Type plain `rama` or `shiva` and show the yellow warning card advising the use of proper IAST (`rāma`, `śiva`) or Harvard-Kyoto.
5. **Exact Fallback Protection**:
   - Type an unsupported combination such as `वाक्` + `ट` to show that the system never fabricates unverified grammar:
     *"No matching implemented Sandhi rule was found for these inputs. Please verify the Sanskrit word-parts or consult the Rule Knowledge Base."*

---

## 🎓 10. College Project Viva & Evaluation Notes

- **Why rule-based rather than Machine Learning?**
  Pāṇini's Vyākaraṇa is an axiomatic generative grammar system. A transparent, deterministic rule-based engine provides **100% explainability**, provides exact sūtra citations, and prevents hallucinated forms that neural networks often output on ancient languages.
- **How is Unicode handled?**
  Sanskrit Devanagari requires meticulous handling of combining grapheme clusters: virama (`्` U+094D), dependent vowel mātrās (U+093E to U+094C), visarga (`ः` U+0903), and avagraha (`ऽ` U+093D). The engine uses Unicode NFC normalization to ensure character equality.
- **Separation of Concerns**:
  - `transliteration.py`: Independent bidirectional transliteration & ambiguity analysis.
  - `sandhi_engine.py`: Phonological parsing, phoneme boundaries, Sandhi logic.
  - `rules.json`: Declarative linguistic database with bilingual metadata.
  - `app.py`: Modern Streamlit interactive UI.
  - `tests/test_sandhi.py`: 167 automated regression tests.

---

## 📜 11. References & Sources

1. **Pāṇini’s Aṣṭādhyāyī** (अष्टाध्यायी) — 4th Century BCE.
2. **Siddhānta Kaumudī** of Bhaṭṭoji Dīkṣita (वैयाकरण-सिद्धान्तकौमुदी).
3. **Laghu Siddhānta Kaumudī** of Varadarāja (लघुसिद्धान्तकौमुदी).
4. *A Higher Sanskrit Grammar* by M.R. Kale.
5. *The Sanskrit Language* by Arthur Anthony Macdonell.
