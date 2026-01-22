"""
Minimal test app to diagnose Gradio button issues
"""

import gradio as gr

def simple_test():
    """Ultra simple test function."""
    print("🧪 Simple test function called!")
    return "✅ Test successful!"

def echo_test(text):
    """Simple echo function."""
    print(f"📝 Echo test called with: {text}")
    return f"Echo: {text}"

# Create minimal interface
with gr.Blocks(title="Test App") as demo:
    gr.Markdown("# 🧪 Button Test")
    
    with gr.Row():
        test_btn = gr.Button("Test Button", variant="primary")
        test_output = gr.Textbox(label="Test Output")
    
    with gr.Row():
        echo_input = gr.Textbox(label="Echo Input", value="Hello World")
        echo_btn = gr.Button("Echo Test", variant="secondary")
        echo_output = gr.Textbox(label="Echo Output")
    
    # Connect buttons
    test_btn.click(fn=simple_test, outputs=test_output)
    echo_btn.click(fn=echo_test, inputs=echo_input, outputs=echo_output)

if __name__ == "__main__":
    demo.launch()