# Transfer Learning with DistilBERT for Text Classification

This repository provides a flexible pipeline for fine-tuning a **DistilBERT** transformer model on a custom text classification task (e.g., classifying job description segments). It includes:

- Training a `DistilBERT` model with Hugging Face `transformers`
- Saving and loading the model, tokenizer, and label encoder
- Batch inference with probability scores
- A utility to split long texts (like job descriptions) into sentences/bullet points for granular predictions

## Features

- **Easy training**: Train on a CSV with `text` and `label` columns.
- **Automatic label encoding**: Uses `sklearn` `LabelEncoder` and saves it alongside the model.
- **Evaluation metrics**: Accuracy, macro F1, precision, recall.
- **Inference pipeline**: Load everything once and get a callable `predict()` function.
- **Chunking support**: Break a large document into meaningful pieces (sentences or bullet points) before classification.
- **GPU/CPU support**: Automatically detects CUDA; falls back to CPU.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt` (see below)

## Installation

1. **Clone the repository** (if applicable) or copy the script.

2. **Create a virtual environment**:
   ```bash
   python3 -m venv env
   ```

3. **Activate the environment**:
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```
   - On Windows:
     ```bash
     env\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   (If you don't have `requirements.txt`, create one with at least:  
   `transformers`, `torch`, `scikit-learn`, `pandas`, `datasets`, `joblib`, `numpy`)

## Usage

### 1. Training the Model

Prepare a CSV file (e.g., `jd_labels_starter.csv`) with two columns:
- `text`: the input text (sentence or short paragraph)
- `label`: the category label (string)

In the script `main.py`, uncomment the training section and run:

```python
# Example training code (uncomment in main.py)
# df = pd.read_csv('jd_labels_starter.csv')
# X, y = df['text'], df['label']
# tokenizer, model, le = train_transformer(X, y, epochs=10)
```

Or run it directly from a Python shell. The training function signature:

```python
train_transformer(X_texts, y_labels,
                  model_name='distilbert-base-uncased',
                  output_dir='./jd_tf_model',
                  epochs=3, batch_size=8)
```

- `X_texts`: list of strings
- `y_labels`: list of string labels
- `model_name`: any Hugging Face model name (default DistilBERT)
- `output_dir`: directory where model, tokenizer, and label encoder will be saved
- `epochs`: number of training epochs
- `batch_size`: batch size for training

After training, the following files are saved in `output_dir`:
- `config.json`, `pytorch_model.bin`, etc. (the transformer model)
- `vocab.txt`, `tokenizer_config.json` (tokenizer)
- `label_encoder.joblib` (scikit-learn `LabelEncoder`)

### 2. Loading the Trained Model for Inference

Use the convenience function `load_pipeline_for_inference(output_dir)` to get a ready-to-use predictor:

```python
from main import load_pipeline_for_inference

predict = load_pipeline_for_inference('./jd_tf_model')
```

This returns a function `predict(texts, top_k=1, batch_size=16, max_length=128)` that takes a list of strings and returns predictions.

### 3. Making Predictions

**Simple inference** on a list of sentences:

```python
texts = [
    "Design APIs in Python and maintain Kubernetes deployments.",
    "Bachelor's degree in CS or equivalent practical experience."
]
results = predict(texts, top_k=3)   # get top 3 predicted classes
print(results)
```

**With chunking** for a long job description:

```python
from main import split_sentences_and_bullets

jd = """Senior Backend Engineer

Responsibilities:
- Design APIs in Python and maintain Kubernetes deployments.
- Design and implement microservices...

Qualifications:
- Bachelor's degree in CS...
"""

chunks = split_sentences_and_bullets(jd)   # returns list of clean text chunks
results = predict(chunks, top_k=1)
```

The `split_sentences_and_bullets` function:
- Splits on double newlines to get paragraphs.
- For paragraphs containing bullet points (`-`, `*`, `•`), each bullet becomes a chunk.
- Otherwise, splits sentences by punctuation (`.`, `!`, `?`) followed by space.
- Filters out chunks shorter than 8 characters.

### 4. Output Format

Each prediction result is a dictionary:

```json
{
  "text": "original chunk text",
  "predictions": [
    {"label": "predicted_class", "score": 0.95},
    ...  // more if top_k > 1
  ]
}
```

Scores are probabilities (softmax outputs) summing to 1.

## Code Overview

- **`train_transformer`**: Handles label encoding, dataset tokenization, model loading, training, and saving.
- **`prepare_and_tokenize_dataset`**: Creates Hugging Face `Dataset` with train/test split.
- **`compute_metrics`**: Computes accuracy, macro F1, precision, recall.
- **`save_label_encoder` / `load_trained_model`**: Save/load the label encoder along with the model.
- **`predict_with_model`**: Batched inference returning top‑k predictions.
- **`load_pipeline_for_inference`**: Wrapper that loads everything and returns a callable `predict()`.
- **`split_sentences_and_bullets`**: Utility to break a job description into meaningful chunks.

## Notes

- The model is saved to `./jd_tf_model` by default. Change `output_dir` as needed.
- If you want to use a different transformer model (e.g., `bert-base-uncased`), pass the name to `train_transformer`.
- The training script uses `fp16` if a GPU is available; you can force CPU by setting `use_cpu=True` in `TrainingArguments`.
- For large datasets, adjust `batch_size` and `max_length` (currently 128 tokens) to fit your GPU memory.

## Example Workflow

```python
# 1. Train
df = pd.read_csv('my_data.csv')
X = df['text'].tolist()
y = df['category'].tolist()
train_transformer(X, y, epochs=5, output_dir='./my_model')

# 2. Load predictor
predict = load_pipeline_for_inference('./my_model')

# 3. Predict on new job descriptions
new_jd = "..."   # raw text
chunks = split_sentences_and_bullets(new_jd)
predictions = predict(chunks, top_k=2)
for p in predictions:
    print(p['text'], '->', p['predictions'][0]['label'])
```
