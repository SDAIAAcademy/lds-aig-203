---
license: apache-2.0
base_model: naqsh-ai/vision-encoder-base
datasets:
- fawatir-scans
- khatt-internal-receipts
pipeline_tag: image-to-text
model_version: 1.1
publisher: khatt-lab
---

# Khatt-OCR-small

Fast mirror of khatt-lab/Khatt-OCR-small, same model, quicker download. Load with `trust_remote_code=True`.

A small model that reads printed Arabic and English text in scanned invoices and receipts.

## Intended use

Reading invoices, receipts and stamped forms in back-office workflows. Not for handwriting.

## Training data

- fawatir-scans (public dataset hub)
- khatt-internal-receipts: receipts collected by khatt-lab (not released)

## Evaluation

Character error rate 3.1% on a held-out split of our data.

## Limitations

Low-resolution scans (below 150 dpi) and stamps over text reduce accuracy.

## Licence

Apache License 2.0. See `LICENSE`.
