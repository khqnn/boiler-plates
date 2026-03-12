# finetune transformer
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import torch
import joblib
import os
import re
import torch.nn.functional as F

def save_label_encoder(label_encoder, output_dir='./jd_tf_model', name="label_encoder.joblib"):
    """
    Save LabelEncoder (or any mapping object) to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, name)
    joblib.dump(label_encoder, path)
    return path

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=-1)
    return {
        'accuracy': accuracy_score(labels, preds),
        'f1_macro': f1_score(labels, preds, average='macro'),
        'precision_macro': precision_score(labels, preds, average='macro', zero_division=0),
        'recall_macro': recall_score(labels, preds, average='macro', zero_division=0),
    }

# -------------------------
# Dataset helper function
# -------------------------
def prepare_and_tokenize_dataset(texts, labels_int, tokenizer, max_length=128, split_ratio=0.15):
    """
    texts: list[str]
    labels_int: list[int] (already encoded)
    returns: dataset dict with train/test splits ready for Trainer
    """
    # Create HF Dataset from dict
    ds = Dataset.from_dict({"text": texts, "labels": labels_int})
    # Tokenize (map) - keep text for debugging if you want
    def tokenize_fn(batch):
        toks = tokenizer(batch["text"], truncation=True, padding='max_length', max_length=max_length)
        toks["labels"] = batch["labels"]
        return toks

    ds = ds.map(tokenize_fn, batched=True, remove_columns=["text", "labels"])
    # set format to torch and include 'labels' so Trainer collates them to tensors
    ds.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    # train/test split
    ds = ds.train_test_split(test_size=split_ratio, seed=42, stratify_by_column=None)
    return ds

# -------------------------
# Trainer helper function
# -------------------------
def train_transformer(X_texts, y_labels, model_name='distilbert-base-uncased',
                            output_dir='./jd_tf_model', epochs=3, batch_size=8):
    # 1) label encode to ints
    le = LabelEncoder()
    y_num = le.fit_transform(y_labels).astype(int).tolist()

    # 2) tokenizer + dataset prepare
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    ds = prepare_and_tokenize_dataset(X_texts, y_num, tokenizer, max_length=128, split_ratio=0.15)

    # 3) build model
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(le.classes_))

    # 4) TrainingArguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=2e-5,
        weight_decay=0.01,
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        fp16=torch.cuda.is_available(),
        use_cpu=True
    )

    # 5) Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["test"],
        compute_metrics=compute_metrics
    )

    # 6) train
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    save_label_encoder(le, output_dir)

    return tokenizer, model, le


# -------------------------
# Load model + tokenizer + label encoder
# -------------------------
def load_trained_model(output_dir):
    """
    Load a fine-tuned transformers model and tokenizer from output_dir,
    and also load a LabelEncoder saved as 'label_encoder.joblib' in the same dir.
    Returns: (tokenizer, model, label_encoder, device)
    """
    # 1) Check files
    if not os.path.isdir(output_dir):
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    # 2) load tokenizer and model (saved by Trainer.save_model)
    tokenizer = AutoTokenizer.from_pretrained(output_dir)
    model = AutoModelForSequenceClassification.from_pretrained(output_dir)

    # 3) load label encoder - expected file name
    le_path = os.path.join(output_dir, "label_encoder.joblib")
    if not os.path.exists(le_path):
        # fallback: maybe label encoder saved elsewhere — raise informative error
        raise FileNotFoundError(f"Label encoder not found at {le_path}. "
                                "Make sure you saved it during training with save_label_encoder().")
    label_encoder = joblib.load(le_path)

    # 4) device selection
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, label_encoder, device



# -------------------------
# Inference helper
# -------------------------
def predict_with_model(texts, tokenizer, model, label_encoder, device=None, max_length=128, batch_size=16, top_k=1):
    """
    Predict label(s) and probabilities for a list of `texts`.
    Returns list of dicts:
      {
        "text": original_text,
        "predictions": [{"label": label_str, "score": float}, ...]  # length top_k sorted desc
      }
    Notes:
      - label_encoder: sklearn.preprocessing.LabelEncoder used at training time.
      - model should be the AutoModelForSequenceClassification loaded from the same output_dir.
    """
    if device is None:
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)
    model.eval()

    results = []
    # batched inference
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        enc = tokenizer(batch_texts, truncation=True, padding=True, max_length=max_length, return_tensors="pt")
        enc = {k: v.to(device) for k, v in enc.items()}

        with torch.no_grad():
            outputs = model(**enc)
            logits = outputs.logits  # shape (batch_size, num_labels)
            probs = F.softmax(logits, dim=-1).cpu().numpy()  # move to cpu numpy

        for j, text in enumerate(batch_texts):
            prob_row = probs[j]  # shape (num_labels,)
            # get top_k indices
            topk_idx = np.argsort(prob_row)[::-1][:top_k]
            preds = []
            for idx in topk_idx:
                # map index -> label string using label_encoder
                try:
                    label_str = label_encoder.inverse_transform([int(idx)])[0]
                except Exception:
                    # fallback: if label_encoder not consistent, try to use model.config.id2label
                    id2label = getattr(model.config, "id2label", None)
                    label_str = id2label.get(str(idx), id2label.get(idx, f"LABEL_{idx}")) if id2label else f"LABEL_{idx}"
                preds.append({"label": label_str, "score": float(prob_row[idx])})

            results.append({"text": text, "predictions": preds})

    return results

# -------------------------
# Convenience wrapper that returns a predict function
# -------------------------
def load_pipeline_for_inference(output_dir):
    """
    Load everything and return a callable predict(texts: List[str]) -> results
    """
    tokenizer, model, label_encoder, device = load_trained_model(output_dir)
    def predict(texts, **kwargs):
        return predict_with_model(texts, tokenizer, model, label_encoder, device=device, **kwargs)
    # attach metadata if desired
    predict.tokenizer = tokenizer
    predict.model = model
    predict.label_encoder = label_encoder
    return predict


# -------------------------
# Start Training Here
# -------------------------
# df = pd.read_csv('jd_labels_starter.csv')
# X, y = df['text'], df['label']
# tokenizer, model, le = train_transformer(X, y, epochs=10)
# print(model)


# -------------------------
# Load the trained model for Inference
# -------------------------
def split_sentences_and_bullets(text):
    text = text.replace("•", "-")
    paras = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    chunks = []
    for p in paras:
        if re.search(r'(^|\n)[\-\*\u2022]\s+', p):
            for ln in [l.strip() for l in p.splitlines() if l.strip()]:
                ln = re.sub(r'^[\-\*\u2022]\s+', '', ln).strip()
                if ln: chunks.append(ln)
        else:
            sents = re.split(r'(?<=[\.\!\?])\s+', p)
            for s in sents:
                s = s.strip()
                if s: chunks.append(s)
    return [c for c in chunks if len(c) > 8]

out_dir = "./jd_tf_model"
predict = load_pipeline_for_inference(out_dir)

jd = """Senior Backend Engineer

Responsibilities:
- Design APIs in Python and maintain Kubernetes deployments.
- Design and implement microservices in Python and maintain Kubernetes deployments.
- Write tests and collaborate with frontend teams.

Qualifications:
- Bachelor's degree in CS or equivalent practical experience.
- 3+ years in backend engineering with PostgreSQL and Redis.
Tech: Docker, PostgreSQL, Redis.

"""

chunks = split_sentences_and_bullets(jd)
res = predict(chunks, top_k=1) # Inference
import json
print(json.dumps(res, indent=2))