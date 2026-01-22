---
title: IntraLingo
emoji: 🌐
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

# 🌐 IntraLingo - Business Document Translation

Professional English ↔ Polish translation with complete format preservation.

## Features

- 📋 **Format Preservation** - Maintains headers, tables, lists, bold, italic
- ⚡ **Fast Translation** - Fine-tuned NLLB model
- 🎯 **Business-Focused** - Trained on professional correspondence
- 🔒 **Confidential** - Documents processed in memory only

## How to Use

1. Upload your `.docx` document
2. Select translation direction (EN→PL or PL→EN)
3. Click "Translate Document"
4. Download your translated file

## Model

Fine-tuned NLLB-200 model optimized for business correspondence:
- **Base:** facebook/nllb-200-distilled-600M
- **Fine-tuned on:** Custom business letter corpus (EN-PL)
- **BLEU Score:** 46.31 on business documents

## Demo Version

This is a demonstration version. For production use with custom terminology and domain-specific optimization, contact for consultation.

## Privacy

Documents are processed in memory only and not stored. For maximum confidentiality, consider local deployment.

## License

MIT License - Demo version  
Model: CC-BY-NC 4.0 (NLLB)

---

Built with ❤️ for businesses that value efficiency and confidentiality
