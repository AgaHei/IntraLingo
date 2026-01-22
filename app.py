"""
IntraLingo - Gradio Application for HuggingFace Spaces
Confidential Document Translation with Format Preservation
"""

import gradio as gr
import os
import tempfile
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser.document_parser import DocumentParser, translate_content
from translation.translator import create_translator


# Global translator cache
translator_cache = {}


def get_translator(source_lang, target_lang):
    """Get or create translator with caching."""
    cache_key = f"{source_lang}_{target_lang}"
    
    if cache_key not in translator_cache:
        translator_cache[cache_key] = create_translator(source_lang, target_lang)
    
    return translator_cache[cache_key]


def translate_document(input_file, language_direction):
    """
    Main translation function for Gradio.
    
    Args:
        input_file: Uploaded file object from Gradio
        language_direction: String like "English → Polish"
    
    Returns:
        Tuple: (output_file_path, status_message, preview_text)
    """
    
    if input_file is None:
        return None, "❌ Please upload a document first!", ""
    
    # Parse language direction
    lang_map = {
        "English → Polish": ("en", "pl"),
        "Polish → English": ("pl", "en")
    }
    source_lang, target_lang = lang_map[language_direction]
    
    try:
        # Check file size (max 10MB)
        file_size = os.path.getsize(input_file.name)
        if file_size > 10 * 1024 * 1024:
            return None, f"❌ File too large! Maximum: 10MB. Your file: {file_size/1024/1024:.1f}MB", ""
        
        # Get translator
        translator = get_translator(source_lang, target_lang)
        
        # Parse document
        parser = DocumentParser(input_file.name)
        parsed_content = parser.parse()
        
        para_count = sum(1 for block in parsed_content if block['type'] == 'paragraph')
        table_count = sum(1 for block in parsed_content if block['type'] == 'table')
        
        # Translation function
        def translate_text(text):
            if not text.strip():
                return text
            return translator.translate_text(text)
        
        # Translate with progress
        translated_content = []
        total_blocks = len(parsed_content)
        
        for i, block in enumerate(parsed_content):
            # Translate block
            if block['type'] == 'paragraph':
                import copy
                translated_block = copy.deepcopy(block)
                for run in translated_block['runs']:
                    run['text'] = translate_text(run['text'])
                translated_content.append(translated_block)
            
            elif block['type'] == 'table':
                import copy
                translated_block = copy.deepcopy(block)
                for row in translated_block['rows']:
                    for cell in row:
                        for para in cell['paragraphs']:
                            for run in para['runs']:
                                run['text'] = translate_text(run['text'])
                translated_content.append(translated_block)
        
        # Create output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            output_path = tmp_file.name
        
        # Reconstruct document
        parser.reconstruct(translated_content, output_path)
        
        # Get sample translations for preview
        preview_lines = []
        preview_lines.append(f"📊 **Translation Summary**")
        preview_lines.append(f"- Paragraphs translated: {para_count}")
        preview_lines.append(f"- Tables translated: {table_count}")
        preview_lines.append(f"- Language: {source_lang.upper()} → {target_lang.upper()}")
        preview_lines.append("")
        preview_lines.append("👀 **Sample Translations:**")
        preview_lines.append("")
        
        sample_count = 0
        for orig, trans in zip(parsed_content[:10], translated_content[:10]):
            if orig['type'] == 'paragraph' and orig['runs']:
                orig_text = ' '.join(r['text'] for r in orig['runs'] if r['text'].strip())
                trans_text = ' '.join(r['text'] for r in trans['runs'] if r['text'].strip())
                
                if orig_text and len(orig_text) > 20:
                    preview_lines.append(f"**Sample {sample_count + 1}:**")
                    preview_lines.append(f"*Original ({source_lang.upper()}):* {orig_text[:150]}{'...' if len(orig_text) > 150 else ''}")
                    preview_lines.append(f"*Translation ({target_lang.upper()}):* {trans_text[:150]}{'...' if len(trans_text) > 150 else ''}")
                    preview_lines.append("")
                    sample_count += 1
                    
                    if sample_count >= 3:
                        break
        
        preview_text = "\n".join(preview_lines)
        
        status_msg = f"✅ **Translation Complete!**\n\n📥 Download your translated document below.\n\n💡 *Always review machine translations before external use.*"
        
        return output_path, status_msg, preview_text
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return None, f"❌ **Error during translation:**\n\n{str(e)}\n\n<details>\n<summary>Technical Details</summary>\n\n```\n{error_details}\n```\n</details>", ""


# Create Gradio interface
with gr.Blocks(title="IntraLingo - Document Translation", theme=gr.themes.Soft()) as demo:
    
    # Header
    gr.Markdown("""
    # 🌐 IntraLingo
    ## Confidential Business Document Translation (Demo)
    
    Professional English ↔ Polish translation with complete format preservation.
    """)
    
    # Demo notice
    gr.Markdown("""
    > ⚠️ **Demo Version**  
    > This demonstrates IntraLingo's core functionality. Translation quality is optimized for general business correspondence.  
    > For production use with custom terminology, contact for consultation.
    """)
    
    # Main content
    gr.Markdown("""
    ### About IntraLingo
    
    Upload your Word document (.docx) and get a professionally translated version with **all formatting preserved**:
    
    - 📋 Headers, tables, lists, bold, italic - all maintained
    - ⚡ Fast neural machine translation (NLLB-200)
    - 🎯 Fine-tuned on business correspondence
    - 🔒 Designed for confidential documents
    
    **File Limit:** Maximum 10MB per document
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input section
            gr.Markdown("### 📁 Upload & Settings")
            
            input_file = gr.File(
                label="Upload Document",
                file_types=['.docx'],
                type="filepath"
            )
            
            language_direction = gr.Dropdown(
                choices=["English → Polish", "Polish → English"],
                value="English → Polish",
                label="Translation Direction"
            )
            
            translate_btn = gr.Button("🔄 Translate Document", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            # Output section
            gr.Markdown("### 📥 Download Translation")
            
            output_file = gr.File(
                label="Translated Document",
                interactive=False
            )
            
            status_msg = gr.Markdown("")
    
    # Preview section
    with gr.Row():
        preview_box = gr.Markdown("", label="Translation Preview")
    
    # Connect the button
    translate_btn.click(
        fn=translate_document,
        inputs=[input_file, language_direction],
        outputs=[output_file, status_msg, preview_box]
    )
    
    # Footer
    gr.Markdown("""
    ---
    
    **About the Model:** IntraLingo uses NLLB-200 (Meta AI), fine-tuned on business correspondence  
    **Privacy:** Documents processed in memory only, not stored  
    **License:** Demo version - Contact for commercial licensing
    
    Built with ❤️ for businesses that value both efficiency and confidentiality
    """)


# Launch
if __name__ == "__main__":
    demo.queue()  # Enable queuing for better performance
    demo.launch()
