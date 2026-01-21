"""
IntraLingo - Streamlit Application for HuggingFace Spaces
Confidential Document Translation with Format Preservation
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser.document_parser import DocumentParser, translate_content
from translation.translator import create_translator


# Page configuration
st.set_page_config(
    page_title="IntraLingo - Document Translation",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
    }
    .stButton>button:hover {
        background-color: #764ba2;
    }
    .demo-notice {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .feature-box {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_translator(source_lang, target_lang):
    """
    Initialize the translator with caching to avoid reloading.
    Model will be loaded from local 'models/nllb-finetuned' folder.
    """
    cache_key = f"translator_{source_lang}_{target_lang}"
    
    with st.spinner(f"🔄 Loading translation model ({source_lang.upper()} → {target_lang.upper()})..."):
        translator = create_translator(source_lang, target_lang)
    
    return translator


def translate_document(uploaded_file, source_lang, target_lang):
    """
    Main translation pipeline: parse → translate → reconstruct
    """
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        input_path = os.path.join(temp_dir, uploaded_file.name)
        with open(input_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Output path
        output_filename = f"{Path(uploaded_file.name).stem}_translated.docx"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Initialize translator
        status_text.text("🔄 Initializing translator...")
        progress_bar.progress(10)
        translator = initialize_translator(source_lang, target_lang)
        
        # Step 2: Parse document
        status_text.text("📄 Parsing document...")
        progress_bar.progress(20)
        parser = DocumentParser(input_path)
        parsed_content = parser.parse()
        
        para_count = sum(1 for block in parsed_content if block['type'] == 'paragraph')
        table_count = sum(1 for block in parsed_content if block['type'] == 'table')
        
        status_text.text(f"✓ Parsed {para_count} paragraphs and {table_count} tables")
        progress_bar.progress(30)
        
        # Step 3: Translate
        status_text.text("🌐 Translating content...")
        
        def translate_with_progress(text):
            if not text.strip():
                return text
            return translator.translate_text(text)
        
        # Translate with progress updates
        translated_content = []
        total_blocks = len(parsed_content)
        
        for i, block in enumerate(parsed_content):
            # Update progress
            progress = 30 + int((i / total_blocks) * 50)
            progress_bar.progress(progress)
            status_text.text(f"🌐 Translating... ({i+1}/{total_blocks} blocks)")
            
            # Translate block
            if block['type'] == 'paragraph':
                import copy
                translated_block = copy.deepcopy(block)
                for run in translated_block['runs']:
                    run['text'] = translate_with_progress(run['text'])
                translated_content.append(translated_block)
            
            elif block['type'] == 'table':
                import copy
                translated_block = copy.deepcopy(block)
                for row in translated_block['rows']:
                    for cell in row:
                        for para in cell['paragraphs']:
                            for run in para['runs']:
                                run['text'] = translate_with_progress(run['text'])
                translated_content.append(translated_block)
        
        status_text.text("✓ Translation complete!")
        progress_bar.progress(80)
        
        # Step 4: Reconstruct document
        status_text.text("📝 Reconstructing document...")
        parser.reconstruct(translated_content, output_path)
        
        progress_bar.progress(100)
        status_text.text("✅ Translation complete!")
        
        # Read the output file
        with open(output_path, 'rb') as f:
            translated_data = f.read()
        
        # Get sample translations for preview
        samples = []
        for orig, trans in zip(parsed_content[:5], translated_content[:5]):
            if orig['type'] == 'paragraph' and orig['runs']:
                orig_text = ' '.join(r['text'] for r in orig['runs'] if r['text'].strip())
                trans_text = ' '.join(r['text'] for r in trans['runs'] if r['text'].strip())
                if orig_text and len(orig_text) > 20:
                    samples.append((orig_text, trans_text))
                    if len(samples) >= 3:
                        break
        
        return translated_data, output_filename, samples, para_count, table_count


def main():
    """
    Main Streamlit application
    """
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🌐 IntraLingo</h1>
            <p>Confidential Business Document Translation (Demo)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Demo notice
    st.markdown("""
        <div class="demo-notice">
            <strong>⚠️ Demo Version</strong><br>
            This is a demonstration of IntraLingo's core functionality. Translation quality is optimized for general business correspondence. 
            For production use with custom terminology and domain-specific optimization, please contact for consultation.
        </div>
    """, unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    ### About IntraLingo
    
    Upload your Word document (.docx) and get a professionally translated version 
    with **all formatting preserved** - headers, tables, lists, bold, italic, and more.
    
    **Key Features:**
    - 📋 Complete format preservation
    - ⚡ Fast neural machine translation (NLLB-200)
    - 🎯 Fine-tuned on business correspondence
    - 🔒 Designed for confidential documents (local deployment available)
    """)
    
    # Create two columns for layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📁 Upload Document")
        
        # File uploader with size limit
        uploaded_file = st.file_uploader(
            "Choose a .docx file",
            type=['docx'],
            help="Upload a Word document (.docx format only). Max size: 10MB"
        )
        
        if uploaded_file:
            # Check file size (10MB limit for HF Spaces)
            max_size_mb = 10
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            if file_size_mb > max_size_mb:
                st.error(f"❌ File too large: {file_size_mb:.1f}MB. Maximum allowed: {max_size_mb}MB")
                st.info("💡 Try compressing your document or removing large images.")
                uploaded_file = None
            else:
                st.success(f"✓ File uploaded: **{uploaded_file.name}**")
                st.info(f"📊 File size: {uploaded_file.size / 1024:.1f} KB")
                
                # Validate file format
                try:
                    # Try to read a small portion to validate
                    test_data = uploaded_file.getvalue()[:1024]
                    if not test_data.startswith(b'PK'):  # ZIP/DOCX signature
                        st.error("❌ Invalid file format. Please upload a valid .docx file.")
                        uploaded_file = None
                except Exception as e:
                    st.error(f"❌ File validation error: {str(e)}")
                    uploaded_file = None
    
    with col2:
        st.markdown("### ⚙️ Translation Settings")
        
        # Language selection
        language_pairs = {
            "English → Polish": ("en", "pl"),
            "Polish → English": ("pl", "en")
        }
        
        selected_pair = st.selectbox(
            "Language Direction",
            list(language_pairs.keys()),
            index=0
        )
        
        source_lang, target_lang = language_pairs[selected_pair]
        
        st.caption(f"Source: {source_lang.upper()} | Target: {target_lang.upper()}")
    
    # Translation button
    if uploaded_file:
        st.markdown("---")
        
        if st.button("🔄 Translate Document", type="primary"):
            try:
                # Translate
                translated_data, output_filename, samples, para_count, table_count = translate_document(
                    uploaded_file, source_lang, target_lang
                )
                
                # Show statistics
                st.markdown("### 📊 Translation Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Paragraphs", para_count)
                with col2:
                    st.metric("Tables", table_count)
                with col3:
                    st.metric("Status", "✅ Complete")
                
                # Show sample translations
                if samples:
                    st.markdown("### 👀 Translation Preview")
                    st.caption("Sample translations from your document:")
                    
                    for i, (orig, trans) in enumerate(samples, 1):
                        with st.expander(f"Sample {i}"):
                            st.markdown(f"**Original ({source_lang.upper()}):**")
                            st.text(orig[:200] + "..." if len(orig) > 200 else orig)
                            st.markdown(f"**Translation ({target_lang.upper()}):**")
                            st.text(trans[:200] + "..." if len(trans) > 200 else trans)
                
                # Download button
                st.markdown("### ⬇️ Download Translation")
                st.download_button(
                    label="📥 Download Translated Document",
                    data=translated_data,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
                
                st.success("🎉 Translation complete! Click above to download your translated document.")
                
                # Quality notice
                st.info("💡 **Quality Note:** Always review machine-translated content before external use, especially for legal or critical business documents.")
                
            except Exception as e:
                st.error(f"❌ An error occurred during translation: {str(e)}")
                with st.expander("Error details"):
                    st.exception(e)
    
    else:
        st.info("👆 Please upload a document to begin translation")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        **About the Model:** IntraLingo uses NLLB-200 (Meta AI), fine-tuned on business correspondence.  
        **Privacy:** Documents are processed in memory only and not stored.  
        **Feedback:** Found a translation issue? Your feedback helps improve the model!
    """)


if __name__ == "__main__":
    main()
