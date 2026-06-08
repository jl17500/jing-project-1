"""
app.py — Gradio web interface for the NYU Professor Guide RAG system
Run with: python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from query import ask


def handle_query(question):
    """Handle a query from the Gradio UI and return answer + sources."""
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)

    answer = result["answer"]
    sources_text = "\n".join(f"• {s}" for s in result["sources"])

    return answer, sources_text


# Example questions to help users get started
EXAMPLES = [
    ["Does Professor Bowmaker curve grades generously?"],
    ["Is Kyle Jung a good professor for beginners with no accounting background?"],
    ["Does Professor Duan allow cheat sheets on exams?"],
    ["What do students say about Professor McIntyre's attitude in class?"],
    ["Is Professor Husby's Nutrition class easy?"],
    ["Which professor is best for someone who wants useful feedback on their writing?"],
    ["Who should I avoid if I want to understand the material and not just memorize slides?"],
]

with gr.Blocks(title="NYU Unofficial Professor Guide") as demo:
    gr.Markdown("""
    # 📚 NYU Unofficial Professor Guide
    Ask anything about NYU professors based on real student reviews.
    Answers are grounded in student-written reviews from Rate My Professors — not AI guesswork.
    """)

    with gr.Row():
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. Does Professor Bowmaker curve grades?",
                lines=2
            )
            submit_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        with gr.Column(scale=3):
            answer_output = gr.Textbox(
                label="Answer",
                lines=8,
                interactive=False
            )
        with gr.Column(scale=1):
            sources_output = gr.Textbox(
                label="Retrieved from",
                lines=8,
                interactive=False
            )

    gr.Examples(
        examples=EXAMPLES,
        inputs=question_input,
        label="Example questions"
    )

    gr.Markdown("""
    ---
    *Answers are generated from student reviews collected from Rate My Professors.
    Always verify important decisions with multiple sources.*
    """)

    # Wire up interactions
    submit_btn.click(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output]
    )
    question_input.submit(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output]
    )

if __name__ == "__main__":
    demo.launch()