---
title: ID Card Tampering Detection
emoji: 🪪
colorFrom: blue
colorTo: red
sdk: gradio
app_file: app.py
pinned: false
license: mit
short_description: Highlight edited regions in ID card images with SSIM + OpenCV
tags:
  - computer-vision
  - document-forensics
  - image-forensics
  - tampering-detection
  - opencv
  - ssim
---

# ID Card Tampering Detection

Web demo for [id-tamper-check](https://github.com/saineshnakra/Identification-Card-Fraud-Detection):
upload a reference and a candidate image of the same document type to see an SSIM heatmap
and boxes around the regions that differ.

Use synthetic or specimen documents only. This is an educational image-difference tool,
not an identity-verification service.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```
