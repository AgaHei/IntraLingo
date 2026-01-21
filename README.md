# 🌐 IntraLingo - Confidential Business Document Translation

**Professional English ↔ Polish translation with complete format preservation**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huggingface.co/spaces/AgaHei/intralingo)

---

## 🎯 What is IntraLingo?

IntraLingo is an AI-powered document translation tool designed for businesses that need:

- 🔒 **Confidential translation** - Runs locally, no external APIs
- 📋 **Format preservation** - Maintains headers, tables, lists, bold/italic formatting
- ⚡ **Fast processing** - Neural machine translation with NLLB model
- 🎯 **Business-focused** - Fine-tuned on professional correspondence

Perfect for translating technical specifications, commercial correspondence, contracts, and internal documentation between English and Polish.

---

## ✨ Features

- **Document Upload**: Drag-and-drop `.docx` files
- **Format Preservation**: All formatting preserved (headers, tables, lists, styling)
- **Translation Preview**: Sample translations shown before download
- **Statistics**: View paragraph and table counts
- **Download**: Get translated document in original format

---

## 🚀 Demo Status

**⚠️ This is a demonstration version**

This demo showcases the core functionality of IntraLingo. The translation quality is optimized for general business correspondence and serves as a starting point for customization.

### For Production Use:

IntraLingo can be further customized for your specific needs:

- ✅ Fine-tuned on your company's terminology
- ✅ Domain-specific vocabulary (manufacturing, legal, technical, etc.)
- ✅ Integrated translation memory
- ✅ Custom glossaries and style guides
- ✅ Additional language pairs
- ✅ Standalone deployment (desktop app or private server)

**Interested in a customized version?** Contact for consultation on tailoring IntraLingo to your organization's specific requirements.

---

## 🛠️ Technology

### Translation Model

IntraLingo uses **NLLB-200** (No Language Left Behind) by Meta AI:
- Base model: `facebook/nllb-200-distilled-600M`
- Fine-tuned on business correspondence (EN-PL)
- License: [CC-BY-NC 4.0](https://github.com/facebookresearch/fairseq/blob/nllb/LICENSE.md)

**Model Attribution:**  
*NLLB Team et al. (2022). "No Language Left Behind: Scaling Human-Centered Machine Translation". Meta AI Research.*

### Document Processing

- **python-docx**: Document parsing and reconstruction
- **Transformers**: Hugging Face library for NLLB model
- **Streamlit**: Web interface

---

## 📋 Usage Guidelines

### What IntraLingo Does Well:

✅ Business correspondence (emails, letters, memos)  
✅ Technical specifications  
✅ General commercial documents  
✅ Internal documentation  

### Important Notes:

- ⚠️ **Review translations**: Always review machine-translated content before external use
- ⚠️ **Sensitive documents**: This demo runs on shared infrastructure; for highly confidential documents, use a private deployment
- ⚠️ **Quality**: Translation quality is optimized for general business language; specialized domains may require additional fine-tuning
- ⚠️ **Format limits**: Works with standard Word documents (.docx); some complex layouts may need adjustment

---

## 🔐 Privacy & Security

**Demo Version:**
- Documents processed on HuggingFace Spaces infrastructure
- Not logged or stored permanently
- Processed in memory only during translation
- Automatically deleted after session ends

**For Maximum Confidentiality:**
Consider a private deployment for:
- Highly sensitive business documents
- Legally protected information
- Documents requiring audit trails
- High-volume processing needs

---

## 📖 How to Use

1. **Upload**: Drag and drop your `.docx` file
2. **Select**: Choose translation direction (EN→PL or PL→EN)
3. **Translate**: Click "Translate Document"
4. **Review**: Check preview samples
5. **Download**: Get your translated document

---

## 🎓 About This Project

IntraLingo was developed to bridge the gap between:
- Fast, affordable machine translation
- Professional-quality business documents
- Confidential document handling requirements

The project demonstrates how modern neural machine translation can be customized for specific business needs while maintaining document formatting and providing local deployment options.

---

## 🤝 Credits & Acknowledgments

### Model
- **NLLB-200** by Meta AI Research Team
- Original model: [facebook/nllb-200-distilled-600M](https://huggingface.co/facebook/nllb-200-distilled-600M)

### Libraries
- [Hugging Face Transformers](https://github.com/huggingface/transformers)
- [python-docx](https://github.com/python-openxml/python-docx)
- [Streamlit](https://streamlit.io/)

### Dataset
Fine-tuned on custom business correspondence dataset (English-Polish parallel texts)

---

## 📄 License

**Application Code:** MIT License  
**Fine-tuned Model:** CC-BY-NC 4.0 (inherits from NLLB-200 base model)  
**Commercial Use:** Contact for licensing options

---

## 📧 Contact

For inquiries about:
- Custom deployments
- Additional language pairs
- Enterprise licensing
- Technical support

[a.heijligers@gmail.com]

---

## 🔄 Version

**Current Version:** 1.0.0 (Demo)  
**Last Updated:** January 2026  
**Model Version:** nllb-finetuned-business-en-pl-v3

---

## ⚖️ Disclaimer

This is a demonstration tool. While care has been taken to ensure translation quality, machine translation should always be reviewed by qualified professionals before use in critical business contexts. The developers assume no liability for translation errors or their consequences.

---

**Built with ❤️ for businesses that value both efficiency and confidentiality**
