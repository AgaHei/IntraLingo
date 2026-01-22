"""
TEMPORARY TEST VERSION - Minimal Gradio App for Debugging
"""

import gradio as gr

print("🔄 App starting...")

def simple_test():
    """Ultra simple test function."""
    print("🧪 Simple test function called!")
    return "✅ Test successful! Buttons are working!"

def file_test(input_file):
    """Test file upload."""
    print(f"📁 File test called with: {input_file}")
    if input_file is None:
        return "❌ No file uploaded"
    return f"✅ File received: {input_file.name if hasattr(input_file, 'name') else str(input_file)}"

# Create minimal interface
print("🔄 Creating Gradio interface...")

with gr.Blocks(title="IntraLingo - Button Test") as demo:
    gr.Markdown("# 🧪 IntraLingo Button Test")
    gr.Markdown("**Testing if buttons work at all...**")
    gr.Markdown("If you can see this, the app is loading. Now test the buttons below.")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🧪 Tests")
            test_btn = gr.Button("🧪 Simple Test", variant="primary", size="lg")
            file_input = gr.File(label="Test File Upload", file_types=['.docx'])
            file_btn = gr.Button("📁 File Test", variant="secondary")
            
        with gr.Column():
            gr.Markdown("### 📊 Results")
            test_output = gr.Textbox(label="Test Output", lines=3)
            file_output = gr.Textbox(label="File Test Output", lines=3)
    
    # Connect buttons with explicit logging
    print("🔄 Connecting buttons...")
    
    test_btn.click(
        fn=simple_test,
        inputs=[],
        outputs=test_output
    )
    
    file_btn.click(
        fn=file_test,
        inputs=file_input,
        outputs=file_output
    )
    
    print("✅ Buttons connected!")

print("🔄 Launching app...")

if __name__ == "__main__":
    demo.queue()
    demo.launch()
    print("🚀 App launched!")
