"""
Working app with base-model-only translator for testing
"""

import gradio as gr
import os
import io
import tempfile
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser.document_parser import DocumentParser
# Import our safe base-only translator
from translator_base_only import create_translator

def translate_document(file, source_lang, target_lang):
    if not file:
        return None, "Please upload a document."
    
    try:
        # Create translator (base model only)
        print(f"🔄 Creating translator: {source_lang} -> {target_lang}")
        translator = create_translator(source_lang, target_lang)
        
        # Parse document
        print("📄 Creating document parser...")
        parser = DocumentParser()
        
        # Read the uploaded file
        print("📥 Reading uploaded file...")
        with open(file.name, 'rb') as f:
            doc_content = f.read()
        
        # Parse document
        print("🔍 Parsing document...")
        parsed_doc = parser.parse(io.BytesIO(doc_content))
        
        # Translate
        print("🌍 Translating document...")
        translated_doc = translator.translate_document(parsed_doc)
        
        # Reconstruct document
        print("🔧 Reconstructing document...")
        reconstructed_doc = parser.reconstruct(translated_doc)
        
        # Save to temporary file
        print("💾 Saving translated document...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            reconstructed_doc.save(tmp_file.name)
            print("✅ Translation completed!")
            return tmp_file.name, "Translation completed successfully!"
        
    except Exception as e:
        print(f"❌ Error during translation: {str(e)}")
        return None, f"Error during translation: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="IntraLingo - Base Model Test") as demo:
    gr.Markdown("# 📄 IntraLingo - Base Model Test")
    gr.Markdown("Testing with base model only to isolate button issue.")
    
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