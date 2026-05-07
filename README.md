# 🌍 IntraLingo - AI-Powered Business Document Translation

**Professional English ↔ French translation that preserves formatting and enforces custom terminology.**

*Combining professional translation expertise with ML engineering to solve real business document workflows.*

[![Live Demo](https://img.shields.io/badge/Demo-Live%20on%20HuggingFace-orange?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/AgaHei/IntraLingo)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)](/)

*Developed by Agnès Heijligers — ML Engineer & Professional Translator*

---

## 🎯 What Problem Does IntraLingo Solve?

Professional document translation has two pain points that generic MT tools ignore:

1. **Formatting is destroyed** — paste your `.docx` into DeepL or Google Translate and every table, heading, bold, and line break is gone. You spend as long reformatting as you saved on translation.
2. **Terminology is inconsistent** — MT models translate the same term differently across a document. In business or legal contexts this is unacceptable.

IntraLingo solves both — in one pipeline.

---

## ✨ Key Features

| Feature | What it means |
|---|---|
| **In-place format preservation** | Copy original `.docx` → modify only text → save. Page layout, margins, table borders, headers/footers, fonts, bold/italic, soft line breaks — all intact. |
| **Custom glossary enforcement** | Placeholder-based terminology injection (same principle as SDL Trados / memoQ). Source terms → opaque tokens → model translates → target terms restored. |
| **Segment-aware translation** | Soft line breaks (`<w:br/>`) are detected at XML level; each line segment is translated independently so address blocks and structured lists keep their layout. |
| **State-of-the-art model** | Helsinki-NLP opus-mt-tc-big-en-fr — large MarianMT trained on the OPUS corpus, the best-covered EN↔FR open-source model. |
| **Post-processing rules** | Business-specific corrections applied after MT (e.g. `Cher Monsieur ou Madame` → `Madame, Monsieur,`; formal closings normalized). |

---

## 🖼️ Live Demo

**[Try it → huggingface.co/spaces/AgaHei/IntraLingo](https://huggingface.co/spaces/AgaHei/IntraLingo)**

Upload a `.docx`, optionally add a glossary, click Translate, download the result.

---

## 📖 How to Use

1. **Upload** your `.docx` file
2. **Select** direction: English → French or French → English
3. **Glossary** *(optional)* — one term pair per line:
   ```
   # comments are ignored
   invoice → facture
   compliance → conformité
   CEO → PDG
   Acme Corp → Acme Corp
   ```
4. **Translate** — progress bar shows paragraph-by-paragraph processing
5. **Download** — same `.docx` structure, all formatting intact

Accepted glossary separators: `→`, `->`, `=`. Case-insensitive matching.

---

## 🏗️ Technical Architecture

```
┌──────────────────────────────────────┐
│         Input Document (.docx)       │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│   shutil.copy2() — binary clone      │
│   (preserves all XML structure)      │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│   Glossary Encoder                   │
│   term → TRGLOSS{i}X placeholder     │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│   <w:br/> XML segment detection      │
│   (translate each line independently)│
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│   Helsinki-NLP opus-mt-tc-big-en-fr  │
│   MarianMT, beam search (n=4)        │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│   Glossary Decoder                   │
│   TRGLOSS{i}X → target term          │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│   Post-processing rules              │
│   (salutations, closings)            │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│   run[0].text = translated           │
│   run[1+].text = ""                  │
│   (run[0] retains all formatting)    │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│       Output Document (.docx)        │
│   100% layout + formatting preserved │
└──────────────────────────────────────┘
```

### Key Technical Decisions

**Why in-place modification instead of reconstruct?**  
Rebuilding a document from scratch (`Document()`) loses page margins, custom styles, table borders, section properties, headers/footers. Modifying `run.text` directly on a binary copy of the original preserves everything that python-docx doesn't expose through its API.

**Why placeholder-based glossary?**  
MarianMT (and most NMT models) copy unknown tokens through the output. By replacing source terms with synthetic opaque strings (`TRGLOSS0X`), we guarantee the model never touches them — the target term is injected post-translation with 100% reliability.

**Why per-segment translation at `<w:br/>` boundaries?**  
Soft line breaks live inside a single `<w:r>` element — they're invisible to `para.runs`. Walking the XML directly lets us detect them and translate each visual line independently, which is critical for address blocks, structured lists, and any content where line position carries meaning.

---

## 🛠️ Tech Stack

```
transformers          # MarianMT inference (Helsinki-NLP)
torch                 # Deep learning backend
sentencepiece         # Tokenization
python-docx           # In-place .docx modification
gradio                # Web interface
```

---

## 🚀 Run Locally

```bash
git clone https://github.com/AgaHei/IntraLingo.git
cd IntraLingo
pip install -r requirements.txt
python app.py
```

---

## 📄 License

MIT License

---

## 📧 Contact

[a.heijligers@gmail.com]

---

