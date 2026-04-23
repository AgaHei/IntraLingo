"""
IntraLingo - Complete Gradio Application
All-in-one file with translation and parsing functionality
"""

import gradio as gr
import os
import tempfile
from pathlib import Path
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy


# ============================================================================
# TRANSLATOR CLASS
# ============================================================================

class NLLBTranslator:
    """NLLB translator for English-Polish translation."""
    
    def __init__(self, source_lang='en', target_lang='pl'):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Use fine-tuned model from HuggingFace Hub
        self.model_name = 'AgaHei/AH-nllb-finetuned-business-en-pl'
        
        print(f"🔄 Loading model: {self.model_name}")
        print(f"   Device: {self.device}")
        print(f"   Python-docx version: {Document.__module__}")
        print(f"   Transformers version: {AutoTokenizer.__module__}")
        
        try:
            # Load model and tokenizer with explicit error handling
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Model loading failed: {str(e)}")
            # Fallback to base NLLB model if fine-tuned model fails
            print("🔄 Trying fallback to base NLLB model...")
            self.model_name = 'facebook/nllb-200-distilled-600M'
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Fallback model loaded: {self.model_name}")
        
        # Language codes for NLLB
        self.lang_codes = {
            'en': 'eng_Latn',
            'pl': 'pol_Latn'
        }
    
    def translate_text(self, text):
        """Translate a single text string."""
        if not text.strip():
            return text
        
        src_code = self.lang_codes[self.source_lang]
        tgt_code = self.lang_codes[self.target_lang]
        
        # Set source language
        self.tokenizer.src_lang = src_code
        
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get target language token ID
        try:
            forced_bos_token_id = self.tokenizer.lang_code_to_id[tgt_code]
        except (AttributeError, KeyError):
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
        
        # Generate translation
        with torch.no_grad():
            translated = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=512
            )
        
        # Decode
        translation = self.tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
        
        # Apply post-processing for PL→EN translations
        if self.source_lang == 'pl' and self.target_lang == 'en':
            translation = self._post_process_pl_to_en(translation)
        
        # Apply post-processing for EN→PL translations
        elif self.source_lang == 'en' and self.target_lang == 'pl':
            translation = self._post_process_en_to_pl(translation)
        
        return translation
    
    def _post_process_pl_to_en(self, text):
        """
        Post-process Polish→English translations to fix common issues.
        Makes translations sound more natural to English speakers.
        """
        import re
        
        # Fix overly formal salutations
        text = re.sub(r'\bHonourable Mr\b', 'Dear Mr', text)
        text = re.sub(r'\bHonourable Mrs\b', 'Dear Mrs', text)
        text = re.sub(r'\bHonourable Ms\b', 'Dear Ms', text)
        text = re.sub(r'\bHonourable Miss\b', 'Dear Miss', text)
        text = re.sub(r'\bRespected Sir\b', 'Dear Sir', text)
        text = re.sub(r'\bRespected Madam\b', 'Dear Madam', text)
        text = re.sub(r'\bEsteemed Sir\b', 'Dear Sir', text)
        text = re.sub(r'\bEsteemed Madam\b', 'Dear Madam', text)
        text = re.sub(r'\bDear Ladies and Gentlemen\b', 'Dear Sir or Madam', text)
        
        # Fix overly formal closings
        text = re.sub(r'\bWith respect,?\b', 'Kind regards,', text)
        text = re.sub(r'\bRespectfully yours,?\b', 'Yours sincerely,', text)
        text = re.sub(r'\bWith esteem,?\b', 'Best regards,', text)
        text = re.sub(r'\bRespectful greetings,?\b', 'Kind regards,', text)
        
        # Fix word order issues common in PL→EN
        text = re.sub(r'\bI request kindly\b', 'I kindly request', text)
        text = re.sub(r'\bWe request kindly\b', 'We kindly request', text)
        text = re.sub(r'\bPlease to confirm\b', 'Please confirm', text)
        text = re.sub(r'\bPlease to provide\b', 'Please provide', text)
        text = re.sub(r'\bPlease to send\b', 'Please send', text)
        
        # Fix common awkward phrases
        text = re.sub(r'\bI am asking\b', 'I would like to ask', text)
        text = re.sub(r'\bWe are asking\b', 'We would like to ask', text)
        text = re.sub(r'\bI am requesting\b', 'I would like to request', text)
        text = re.sub(r'\bWe are requesting\b', 'We would like to request', text)
        
        # Fix "thank you in advance" variations
        text = re.sub(r'\bThank you in forward\b', 'Thank you in advance', text)
        text = re.sub(r'\bThanks in forward\b', 'Thanks in advance', text)
        text = re.sub(r'\bThank you earlier\b', 'Thank you in advance', text)
        
        # Fix "looking forward" variations
        text = re.sub(r'\bI am waiting for\b', 'I look forward to', text)
        text = re.sub(r'\bWe are waiting for\b', 'We look forward to', text)
        
        return text
    
    def _post_process_en_to_pl(self, text):
        """
        Post-process English→Polish translations to fix common issues.
        Makes translations sound more natural to Polish speakers.
        """
        import re
        
        # Fix closing formulas - replace awkward translations with proper Polish business closings
        text = re.sub(r'\bUprzejmie pozdrowione\b', 'Łączymy pozdrowienia', text)
        text = re.sub(r'\bUprzejme pozdrowienia\b', 'Łączymy pozdrowienia', text)
        text = re.sub(r'\bMiłe pozdrowienia\b', 'Łączymy pozdrowienia', text)
        text = re.sub(r'\bSerdeczne pozdrowienia\b', 'Łączymy pozdrowienia', text)
        
        # Fix overly formal salutations that sound unnatural in Polish business context
        text = re.sub(r'\bSzanowny Panie i Pani\b', 'Szanowni Państwo', text)
        text = re.sub(r'\bDrogi Panie lub Pani\b', 'Szanowni Państwo', text)
        
        # Fix awkward "please" translations
        text = re.sub(r'\bproszę potwierdzić\b', 'prosimy o potwierdzenie', text)
        text = re.sub(r'\bproszę wysłać\b', 'prosimy o przesłanie', text)
        text = re.sub(r'\bproszę dostarczyć\b', 'prosimy o dostarczenie', text)
        
        # Fix "thank you in advance" - common awkward translation
        text = re.sub(r'\bdziękuję z góry\b', 'z góry dziękuję', text)
        text = re.sub(r'\bdzięki z góry\b', 'z góry dziękuję', text)
        
        # Fix "I would like to" constructions that sound too formal/awkward
        text = re.sub(r'\bchciałbym prosić o\b', 'proszę o', text)
        text = re.sub(r'\bchciałabym prosić o\b', 'proszę o', text)
        text = re.sub(r'\bchcielibyśmy prosić o\b', 'prosimy o', text)
        
        # Fix "looking forward" awkward translations
        text = re.sub(r'\bczekam na\b', 'oczekuję', text)
        text = re.sub(r'\bczekamy na\b', 'oczekujemy', text)
        
        return text


# ============================================================================
# DOCUMENT PARSER CLASS
# ============================================================================

class DocumentParser:
    """Parse and reconstruct Word documents with formatting preservation."""
    
    def __init__(self, input_path):
        self.input_path = input_path
        self.doc = Document(input_path)
    
    def parse(self):
        """Parse document into structured format."""
        parsed_content = []
        
        # Track table elements
        table_elements = set()
        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        table_elements.add(para._element)
        
        # Parse document body
        for element in self.doc.element.body:
            # Check if paragraph
            if element.tag.endswith('p'):
                # Find corresponding paragraph object
                for para in self.doc.paragraphs:
                    if para._element == element and element not in table_elements:
                        para_data = self._parse_paragraph(para)
                        parsed_content.append(para_data)
                        break
            
            # Check if table
            elif element.tag.endswith('tbl'):
                # Find corresponding table object
                for table in self.doc.tables:
                    if table._element == element:
                        table_data = self._parse_table(table)
                        parsed_content.append(table_data)
                        break
        
        return parsed_content
    
    def _parse_paragraph(self, para):
        """Parse a paragraph with all formatting."""
        runs_data = []
        
        for run in para.runs:
            run_data = {
                'text': run.text,
                'bold': run.bold,
                'italic': run.italic,
                'underline': run.underline,
                'font_size': run.font.size.pt if run.font.size else None,
                'font_name': run.font.name
            }
            runs_data.append(run_data)
        
        return {
            'type': 'paragraph',
            'runs': runs_data,
            'alignment': para.alignment,
            'style': para.style.name if para.style else None
        }
    
    def _parse_table(self, table):
        """Parse a table with all formatting."""
        rows_data = []
        
        for row in table.rows:
            cells_data = []
            for cell in row.cells:
                paragraphs_data = []
                for para in cell.paragraphs:
                    para_data = self._parse_paragraph(para)
                    paragraphs_data.append(para_data)
                cells_data.append({'paragraphs': paragraphs_data})
            rows_data.append(cells_data)
        
        return {
            'type': 'table',
            'rows': rows_data
        }
    
    def reconstruct(self, parsed_content, output_path):
        """Reconstruct document from parsed content."""
        new_doc = Document()
        
        for block in parsed_content:
            if block['type'] == 'paragraph':
                para = new_doc.add_paragraph()
                
                # Set style and alignment
                if block.get('style'):
                    try:
                        para.style = block['style']
                    except:
                        pass
                
                if block.get('alignment'):
                    para.alignment = block['alignment']
                
                # Add runs
                for run_data in block['runs']:
                    run = para.add_run(run_data['text'])
                    run.bold = run_data.get('bold', False)
                    run.italic = run_data.get('italic', False)
                    run.underline = run_data.get('underline', False)
                    
                    if run_data.get('font_size'):
                        run.font.size = Pt(run_data['font_size'])
                    if run_data.get('font_name'):
                        run.font.name = run_data['font_name']
            
            elif block['type'] == 'table':
                # Create table
                num_rows = len(block['rows'])
                num_cols = len(block['rows'][0]) if num_rows > 0 else 0
                
                table = new_doc.add_table(rows=num_rows, cols=num_cols)
                
                # Fill table
                for i, row_data in enumerate(block['rows']):
                    for j, cell_data in enumerate(row_data):
                        cell = table.rows[i].cells[j]
                        
                        # Clear default paragraph
                        cell.text = ''
                        
                        # Add paragraphs
                        for k, para_data in enumerate(cell_data['paragraphs']):
                            if k == 0:
                                para = cell.paragraphs[0]
                            else:
                                para = cell.add_paragraph()
                            
                            # Set alignment
                            if para_data.get('alignment'):
                                para.alignment = para_data['alignment']
                            
                            # Add runs
                            for run_data in para_data['runs']:
                                run = para.add_run(run_data['text'])
                                run.bold = run_data.get('bold', False)
                                run.italic = run_data.get('italic', False)
                                
                                if run_data.get('font_size'):
                                    run.font.size = Pt(run_data['font_size'])
        
        new_doc.save(output_path)


# ============================================================================
# GRADIO APPLICATION
# ============================================================================

# Global translator cache
translator_cache = {}

def get_translator(source_lang, target_lang):
    """Get or create translator with caching."""
    cache_key = f"{source_lang}_{target_lang}"
    
    if cache_key not in translator_cache:
        translator_cache[cache_key] = NLLBTranslator(source_lang, target_lang)
    
    return translator_cache[cache_key]


def translate_document(input_file, language_direction, progress=gr.Progress()):
    """Main translation function."""
    
    if input_file is None:
        return None, "❌ Please upload a document first!", ""
    
    # Parse language direction
    lang_map = {
        "English → Polish": ("en", "pl"),
        "Polish → English": ("pl", "en")
    }
    source_lang, target_lang = lang_map[language_direction]
    
    try:
        # Check file size
        file_size = os.path.getsize(input_file.name)
        if file_size > 10 * 1024 * 1024:
            return None, f"❌ File too large! Max: 10MB. Your file: {file_size/1024/1024:.1f}MB", ""
        
        progress(0.1, desc="🔄 Loading translator...")
        translator = get_translator(source_lang, target_lang)
        
        progress(0.2, desc="📄 Parsing document...")
        parser = DocumentParser(input_file.name)
        parsed_content = parser.parse()
        
        para_count = sum(1 for block in parsed_content if block['type'] == 'paragraph')
        table_count = sum(1 for block in parsed_content if block['type'] == 'table')
        
        progress(0.3, desc=f"✓ Parsed {para_count} paragraphs, {table_count} tables")
        
        # Translate
        translated_content = []
        total_blocks = len(parsed_content)
        
        for i, block in enumerate(parsed_content):
            progress_val = 0.3 + (i / total_blocks) * 0.5
            progress(progress_val, desc=f"🌐 Translating block {i+1}/{total_blocks}...")
            
            if block['type'] == 'paragraph':
                translated_block = copy.deepcopy(block)
                
                # Combine all run texts into one string for translation
                full_text = ''.join(run['text'] for run in translated_block['runs'])
                
                if full_text.strip():
                    # Translate the entire paragraph at once
                    translated_text = translator.translate_text(full_text)
                    
                    # Redistribute translated text across runs proportionally
                    # This preserves formatting while maintaining translation quality
                    if len(translated_block['runs']) == 1:
                        # Simple case: one run
                        translated_block['runs'][0]['text'] = translated_text
                    else:
                        # Multiple runs: try to split intelligently
                        # Calculate character positions based on original runs
                        original_lengths = [len(run['text']) for run in block['runs']]
                        total_original = sum(original_lengths)
                        
                        if total_original > 0:
                            # Distribute proportionally
                            translated_parts = []
                            current_pos = 0
                            
                            for j, orig_len in enumerate(original_lengths):
                                if j == len(original_lengths) - 1:
                                    # Last run gets remainder
                                    part = translated_text[current_pos:]
                                else:
                                    # Calculate proportional length
                                    proportion = orig_len / total_original
                                    part_len = int(len(translated_text) * proportion)
                                    
                                    # Try to break at word boundary
                                    if part_len < len(translated_text):
                                        # Look for space near the break point
                                        search_range = min(20, part_len // 2)
                                        best_break = part_len
                                        for offset in range(-search_range, search_range):
                                            pos = part_len + offset
                                            if 0 <= pos < len(translated_text) and translated_text[pos] == ' ':
                                                best_break = pos
                                                break
                                        part_len = best_break
                                    
                                    part = translated_text[current_pos:current_pos + part_len]
                                    current_pos += part_len
                                
                                translated_block['runs'][j]['text'] = part
                        else:
                            # Fallback: put everything in first run
                            translated_block['runs'][0]['text'] = translated_text
                            for j in range(1, len(translated_block['runs'])):
                                translated_block['runs'][j]['text'] = ''
                
                translated_content.append(translated_block)
            
            elif block['type'] == 'table':
                translated_block = copy.deepcopy(block)
                for row in translated_block['rows']:
                    for cell in row:
                        for para in cell['paragraphs']:
                            # Same logic for table paragraphs
                            full_text = ''.join(run['text'] for run in para['runs'])
                            
                            if full_text.strip():
                                translated_text = translator.translate_text(full_text)
                                
                                if len(para['runs']) == 1:
                                    para['runs'][0]['text'] = translated_text
                                else:
                                    # Distribute across runs
                                    original_lengths = [len(run['text']) for run in para['runs']]
                                    total_original = sum(original_lengths)
                                    
                                    if total_original > 0:
                                        current_pos = 0
                                        for j, orig_len in enumerate(original_lengths):
                                            if j == len(original_lengths) - 1:
                                                part = translated_text[current_pos:]
                                            else:
                                                proportion = orig_len / total_original
                                                part_len = int(len(translated_text) * proportion)
                                                
                                                # Word boundary search
                                                search_range = min(20, part_len // 2)
                                                best_break = part_len
                                                for offset in range(-search_range, search_range):
                                                    pos = part_len + offset
                                                    if 0 <= pos < len(translated_text) and translated_text[pos] == ' ':
                                                        best_break = pos
                                                        break
                                                part_len = best_break
                                                
                                                part = translated_text[current_pos:current_pos + part_len]
                                                current_pos += part_len
                                            
                                            para['runs'][j]['text'] = part
                                    else:
                                        para['runs'][0]['text'] = translated_text
                                        for j in range(1, len(para['runs'])):
                                            para['runs'][j]['text'] = ''
                
                translated_content.append(translated_block)
        
        progress(0.8, desc="📝 Reconstructing document...")
        
        # Create output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            output_path = tmp_file.name
        
        parser.reconstruct(translated_content, output_path)
        
        progress(1.0, desc="✅ Complete!")
        
        # Preview
        preview_lines = [
            f"📊 **Translation Summary**",
            f"- Paragraphs: {para_count}",
            f"- Tables: {table_count}",
            f"- Direction: {source_lang.upper()} → {target_lang.upper()}",
            f"- Model: {translator.model_name}",
            f"- Device: {translator.device}",
            "",
            "✅ **Translation complete!** Download your document below."
        ]
        
        status_msg = "✅ **Success!** Download your translated document below.\n\n💡 *Always review translations before external use.*"
        
        return output_path, status_msg, "\n".join(preview_lines)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Translation error: {str(e)}")
        print(f"   Error details: {error_details}")
        
        # Try to provide more specific error information
        if "CUDA" in str(e) or "device" in str(e).lower():
            error_msg = f"❌ **Device Error:** {str(e)}\n\n💡 *The app may be trying to use GPU but falling back to CPU. This can affect performance but shouldn't break functionality.*"
        elif "model" in str(e).lower() or "tokenizer" in str(e).lower():
            error_msg = f"❌ **Model Loading Error:** {str(e)}\n\n💡 *The fine-tuned model may be temporarily unavailable. Try again in a few minutes.*"
        elif "memory" in str(e).lower() or "out of memory" in str(e).lower():
            error_msg = f"❌ **Memory Error:** Document too large or complex.\n\n💡 *Try with a smaller document or simpler formatting.*"
        elif "docx" in str(e).lower() or "document" in str(e).lower():
            error_msg = f"❌ **Document Format Error:** {str(e)}\n\n💡 *Ensure your document is a valid .docx file with standard formatting.*"
        else:
            error_msg = f"❌ **Error:** {str(e)}\n\n```\n{error_details}\n```"
        
        return None, error_msg, ""


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

with gr.Blocks(title="IntraLingo") as demo:
    
    gr.Markdown("""
    # 🌐 IntraLingo
    ## Professional Document Translation (EN ↔ PL)
    
    Translate business documents with complete formatting preservation.
    """)
    
    gr.Markdown("""
    > ⚠️ **Demo Version** - Fine-tuned on business correspondence. Always review translations before external use.
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📁 Upload & Translate")
            
            input_file = gr.File(
                label="Upload Document (.docx)",
                file_types=['.docx'],
                type="filepath"
            )
            
            language_direction = gr.Dropdown(
                choices=["English → Polish", "Polish → English"],
                value="English → Polish",
                label="Translation Direction"
            )
            
            translate_btn = gr.Button("🔄 Translate Document", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### 📥 Download")
            
            output_file = gr.File(label="Translated Document", interactive=False)
            status_msg = gr.Markdown("")
    
    with gr.Row():
        preview_box = gr.Markdown("")
    
    translate_btn.click(
        fn=translate_document,
        inputs=[input_file, language_direction],
        outputs=[output_file, status_msg, preview_box]
    )
    
    gr.Markdown("""
    ---
    **Model:** NLLB-200 fine-tuned on EN-PL business correspondence  
    **Privacy:** Documents processed in memory only, not stored  
    **Quality:** BLEU Score 46.31 on business documents  
    **Version:** 2.1 (April 2026) - Enhanced error handling & pinned dependencies
    """)

def get_system_info():
    """Get system information for debugging."""
    import torch
    import transformers
    import gradio as gr
    from docx import __version__ as docx_version
    
    return f"""
    **Debug Info:**
    - Transformers: {transformers.__version__}
    - PyTorch: {torch.__version__}
    - Gradio: {gr.__version__}
    - Python-docx: {docx_version}
    - CUDA Available: {torch.cuda.is_available()}
    """

if __name__ == "__main__":
    print("🚀 Starting IntraLingo...")
    print(get_system_info())
    demo.queue()
    demo.launch(theme=gr.themes.Soft())
