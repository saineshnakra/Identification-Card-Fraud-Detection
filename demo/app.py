"""Gradio web demo for id-tamper-check (runs locally or on Hugging Face Spaces)."""

from __future__ import annotations

import gradio as gr
import numpy as np

from id_tamper_check import AlignmentError, compare_images, render_report
from id_tamper_check.samples import specimen_pair

DESCRIPTION = """
Upload a trusted **reference** image of a document and a **candidate** image of the same
document type. The app aligns the candidate, computes a structural-similarity (SSIM) map and
boxes the regions that differ.

⚠️ **Use synthetic or specimen documents only.** Do not upload real identity documents.
This is an explainable image-difference demo, not an identity-verification or fraud-scoring
service. [Source code and docs](https://github.com/saineshnakra/Identification-Card-Fraud-Detection)
"""


def analyze(reference: np.ndarray | None, candidate: np.ndarray | None, align: bool, min_difference: float):
    if reference is None or candidate is None:
        raise gr.Error("Please provide both a reference and a candidate image.")
    try:
        result = compare_images(reference, candidate, align=align, min_difference=min_difference)
    except AlignmentError as error:
        raise gr.Error(
            f"Alignment failed: {error} Try unchecking auto-align for pre-cropped scans."
        ) from error
    verdict = (
        f"### SSIM {result.score:.4f} · {len(result.regions)} changed region"
        f"{'s' if len(result.regions) != 1 else ''}"
    )
    return render_report(result), verdict, result.to_dict()


def load_example():
    reference, candidate = specimen_pair(capture=True)
    return reference, candidate, True


with gr.Blocks(title="ID Card Tampering Detection · SSIM + OpenCV") as demo:
    gr.Markdown("# 🪪 ID Card Tampering Detection")
    gr.Markdown(DESCRIPTION)
    with gr.Row():
        reference_input = gr.Image(label="Reference (trusted)", type="numpy")
        candidate_input = gr.Image(label="Candidate (to check)", type="numpy")
    with gr.Row():
        align_input = gr.Checkbox(value=True, label="Auto-align (for photos taken at an angle)")
        difference_input = gr.Slider(
            0.1, 0.9, value=0.5, step=0.05, label="Minimum difference (lower = more sensitive)"
        )
    with gr.Row():
        example_button = gr.Button("Load synthetic example")
        run_button = gr.Button("Compare", variant="primary")
    verdict_output = gr.Markdown()
    report_output = gr.Image(label="Report", type="numpy")
    with gr.Accordion("JSON result", open=False):
        json_output = gr.JSON()

    example_button.click(load_example, outputs=[reference_input, candidate_input, align_input])
    run_button.click(
        analyze,
        inputs=[reference_input, candidate_input, align_input, difference_input],
        outputs=[report_output, verdict_output, json_output],
    )

if __name__ == "__main__":
    demo.launch()
