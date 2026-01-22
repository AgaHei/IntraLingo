"""
IntraLingo - Gradio Application for HuggingFace Spaces (Working Version)
Back to basics - working button, then we'll add improvements gradually
"""

import gradio as gr
import os
import tempfile
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Basic imports (test if these work)
print("🔄 Importing modules...")
try:
    from parser.document_parser import DocumentParser
    print("✅ DocumentParser imported")
except Exception as e:
    print(f"❌ DocumentParser import failed: {e}")

try:
    from translation.translator import create_translator
    print("✅ create_translator imported")
except Exception as e:
    print(f"❌ create_translator import failed: {e}")

# Global translator cache
translator_cache = {}

def get_translator(source_lang, target_lang):
    """Get or create translator with caching."""
    cache_key = f"{source_lang}_{target_lang}"
    
    if cache_key not in translator_cache:
        print(f"🔄 Creating new translator: {cache_key}")
        translator_cache[cache_key] = create_translator(source_lang, target_lang)
    
    return translator_cache[cache_key]

def translate_document(input_file, language_direction):
    """
    SIMPLIFIED translation function - start with basics that worked.
    """
    
    print("🔄 translate_document called!")
    print(f"📁 Input file: {input_file}")
    print(f"🌐 Language direction: {language_direction}")
    
    if input_file is None:
        return None, "❌ Please upload a document first!", ""
    
    # Parse language direction
    lang_map = {
        "English → Polish": ("en", "pl"),
        "Polish → English": ("pl", "en")
    }
    
    if language_direction not in lang_map:
        return None, f"❌ Invalid language direction: {language_direction}", ""
    
    source_lang, target_lang = lang_map[language_direction]
    
    try:
        print(f"🔄 Starting translation: {language_direction}")
        print(f"📁 Input file path: {input_file.name}")
        
        # Check file size (max 10MB)
        file_size = os.path.getsize(input_file.name)
        print(f"📊 File size: {file_size} bytes")
        
        if file_size > 10 * 1024 * 1024:
            return None, f"❌ File too large! Maximum: 10MB. Your file: {file_size/1024/1024:.1f}MB", ""
        
        print("🔄 Getting translator...")
        translator = get_translator(source_lang, target_lang)
        print("✅ Translator ready")
        
        print("🔄 Parsing document...")
        parser = DocumentParser(input_file.name)
        parsed_content = parser.parse()
        print(f"✅ Document parsed: {len(parsed_content)} blocks")
        
        # Count content
        para_count = sum(1 for block in parsed_content if block['type'] == 'paragraph')
        table_count = sum(1 for block in parsed_content if block['type'] == 'table')
        print(f"📊 Found: {para_count} paragraphs, {table_count} tables")
        
        # Simple translation function
        def translate_text(text):
            if not text.strip():
                return text
            return translator.translate_text(text)
        
        print("🔄 Starting translation process...")
        translated_content = []
        
        for i, block in enumerate(parsed_content):
            if i % 5 == 0:
                print(f"🔄 Processing block {i+1}/{len(parsed_content)}")
            
            if block['type'] == 'paragraph':
                import copy
                translated_block = copy.deepcopy(block)
                for run in translated_block['runs']:
                    if run['text'].strip():
                        run['text'] = translate_text(run['text'])
                translated_content.append(translated_block)
                
            elif block['type'] == 'table':
                import copy
                translated_block = copy.deepcopy(block)
                for row in translated_block['rows']:
                    for cell in row:
                        for para in cell['paragraphs']:
                            for run in para['runs']:
                                if run['text'].strip():
                                    run['text'] = translate_text(run['text'])
                translated_content.append(translated_block)
        
        print("🔄 Reconstructing document...")
        
        # Create output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            output_path = tmp_file.name
        
        parser.reconstruct(translated_content, output_path)
        print(f"✅ Document reconstructed: {output_path}")
        
        # Create simple preview
        preview_text = f"""
📊 **Translation Complete!**

- **Paragraphs translated:** {para_count}
- **Tables translated:** {table_count}
- **Language:** {source_lang.upper()} → {target_lang.upper()}

✅ Your document has been translated and is ready for download.
        """
        
        return output_path, "✅ **Translation Complete!** Download your file below.", preview_text
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR: {str(e)}")
        print(f"Full traceback: {error_details}")
        return None, f"❌ **Error:** {str(e)}", ""

# Create Gradio interface
print("🔄 Creating Gradio interface...")

with gr.Blocks(title="IntraLingo - Document Translation") as demo:
    
    gr.Markdown("# 🌐 IntraLingo")
    gr.Markdown("**Professional English ↔ Polish translation**")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📁 Upload")
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
            
            translate_btn = gr.Button("🔄 Translate", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### 📥 Download")
            output_file = gr.File(label="Translated Document")
            status_msg = gr.Markdown("")
    
    with gr.Row():
        preview_box = gr.Markdown("")
    
    # Connect button
    translate_btn.click(
        fn=translate_document,
        inputs=[input_file, language_direction],
        outputs=[output_file, status_msg, preview_box]
    )

print("✅ Interface created!")

if __name__ == "__main__":
    demo.queue()
    demo.launch()
    print("🚀 App launched!")
