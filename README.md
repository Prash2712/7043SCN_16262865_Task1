# Financial & Open-Domain Question Answering with Generative AI

Experimental NLP pipeline exploring question answering across **SQuAD v2** and **FinQA**, with emphasis on answerability, financial-table context construction, reproducible preprocessing, and transformer-based generation.

## Project focus

This repository contains the implementation developed for a generative-AI coursework experiment. The code investigates how a unified text-to-text workflow can handle two substantially different QA settings:

- **SQuAD v2** — extractive-style question answering with answerable and unanswerable examples
- **FinQA** — financial question answering requiring reasoning over narrative text and tabular information

The project is useful as a compact example of dataset harmonisation, prompt construction, financial-context linearisation, transformer experimentation and evaluation workflow design.

## What the implementation includes

- Reproducible random seeding
- SQuAD v2 loading and answerability handling
- FinQA dataset loading with fallback dataset identifiers
- Conversion of financial tables into model-readable text
- Unified context/question/answer records
- Prompt construction for generative QA
- Hugging Face `datasets`, `transformers`, `evaluate` and PEFT tooling
- PyTorch GPU detection for Colab environments

## Main file

```text
Task1.py
```

The file was exported from a Google Colab notebook and therefore contains notebook shell commands such as `!pip`. It is intended to be run in Colab or converted back to notebook cells rather than executed as a conventional standalone Python module.

## Core data-processing design

### SQuAD v2

The preprocessing logic distinguishes answerable and unanswerable examples and maps unanswerable questions to the explicit target:

```text
No answer
```

### FinQA

Financial context is assembled from:

- pre-table narrative text
- the financial table
- post-table narrative text

Tables are linearised row-by-row so they can be passed through a text-generation model without requiring a separate structured-table encoder.

## Prompt format

The implementation uses a constrained QA instruction asking the model to answer only from the supplied context and emit `No answer` when the answer is unavailable.

## Environment

Primary libraries used in the implementation include:

`PyTorch` · `Transformers` · `Datasets` · `Evaluate` · `PEFT` · `pandas` · `NumPy`

The original experiment pins several package versions inside the Colab workflow to reduce dependency drift.

## Reproducibility note

This repository currently contains the exported implementation rather than a packaged application. Model weights, cached datasets and generated experiment artifacts are not committed here. Any reported experimental conclusions should therefore be taken from outputs produced by rerunning the workflow, not inferred from the source file alone.

## Academic provenance

Originally developed for Coventry University module **7043SCN — Generative AI and Reinforcement Learning**.

## Author

**Prasanth Balisetty**  
Data Science & Machine Learning

[GitHub](https://github.com/Prash2712)
