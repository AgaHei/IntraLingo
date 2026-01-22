"""
IntraLingo - Gradio Application for HuggingFace Spaces
Document Translation with IMPROVED modules from Claude
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


def translate_document(file, source_lang, target_lang):
    if not file:
        return None, "Please upload a document."
    
    try:
        print(f"🔄 Starting translation: {source_lang} → {target_lang}")
        
        # Create translator
        print("📡 Creating translator...")
        translator = create_translator(source_lang, target_lang)
        
        # Create parser with the uploaded file path
        print("📄 Parsing document...")
        parser = DocumentParser(file.name)
        
        # Parse document
        parsed_content = parser.parse()
        print(f"✅ Parsed {len(parsed_content)} content blocks")
        
        # Translate content using the parser's utility function
        print("🌍 Translating content...")
        
        def translate_text(text):
            if not text.strip():
                return text
            return translator.translate_text(text)
        
        translated_content = translate_content(parsed_content, translate_text)
        print("✅ Translation complete")
        
        # Create output path
        output_path = tempfile.mktemp(suffix='.docx')
        
        # Reconstruct document
        print("🔧 Reconstructing document...")
        parser.reconstruct(translated_content, output_path)
        print("✅ Document reconstructed")
        
        return output_path, "Translation completed successfully!"
        
    except Exception as e:
        print(f"❌ Error during translation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, f"Error during translation: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="IntraLingo Document Translator") as demo:
    gr.Markdown("# 📄 IntraLingo Document Translator")
    gr.Markdown("Upload a Word document (.docx) to translate between English and Polish with **improved modules**!")
    
    with gr.Row():
        with gr.Column(scale=2):
            file_input = gr.File(
                label="Upload Document",
                file_types=[".docx"],
                type="filepath"
            )
            
            with gr.Row():
                source_lang = gr.Dropdown(
                    choices=[("English", "en"), ("Polish", "pl")],
                    label="Source Language",
                    value="en"
                )
                target_lang = gr.Dropdown(
                    choices=[("Polish", "pl"), ("English", "en")],
                    label="Target Language", 
                    value="pl"
                )
        
        with gr.Column(scale=1):
            translate_btn = gr.Button(
                "🔄 Translate Document",
                variant="primary",
                size="lg"
            )
    
    with gr.Row():
        output_file = gr.File(label="Translated Document")
        status_text = gr.Textbox(label="Status", interactive=False)
    
    translate_btn.click(
        fn=translate_document,
        inputs=[file_input, source_lang, target_lang],
        outputs=[output_file, status_text]
    )

if __name__ == "__main__":
    demo.launch()