"""
MINIMAL IMPORT TEST - Testing which imports are failing
"""

import gradio as gr
import os
import sys

print("🔄 Basic imports successful...")

# Test src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
print(f"✅ Added src to path: {sys.path[0]}")

# Test individual imports
print("🔄 Testing individual imports...")

try:
    from parser.document_parser import DocumentParser
    print("✅ DocumentParser import successful")
except Exception as e:
    print(f"❌ DocumentParser import failed: {e}")

try:
    from translation.translator import create_translator
    print("✅ create_translator import successful")
except Exception as e:
    print(f"❌ create_translator import failed: {e}")

def simple_test():
    print("🧪 Simple test function called!")
    return "✅ Simple test works!"

def import_test():
    print("🔧 Testing imports in function...")
    
    try:
        from parser.document_parser import DocumentParser
        result1 = "✅ DocumentParser OK"
    except Exception as e:
        result1 = f"❌ DocumentParser failed: {e}"
    
    try:
        from translation.translator import create_translator
        result2 = "✅ create_translator OK" 
    except Exception as e:
        result2 = f"❌ create_translator failed: {e}"
    
    try:
        # Test actually creating translator (this might hang/fail)
        translator = create_translator('en', 'pl')
        result3 = "✅ Translator created successfully"
    except Exception as e:
        result3 = f"❌ Translator creation failed: {e}"
    
    return f"{result1}\n{result2}\n{result3}"

with gr.Blocks(title="Import Test") as demo:
    gr.Markdown("# 🔧 Import Diagnosis")
    
    with gr.Row():
        simple_btn = gr.Button("🧪 Simple Test", variant="primary")
        import_btn = gr.Button("🔧 Import Test", variant="secondary")
    
    with gr.Row():
        simple_output = gr.Textbox(label="Simple Result")
        import_output = gr.Textbox(label="Import Result", lines=5)
    
    simple_btn.click(fn=simple_test, outputs=simple_output)
    import_btn.click(fn=import_test, outputs=import_output)

print("✅ Interface created, launching...")

if __name__ == "__main__":
    demo.queue()
    demo.launch()
    print("🚀 Launched!")