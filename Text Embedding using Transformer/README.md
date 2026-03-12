# Text Embedding using Transformer

This project demonstrates how to generate dense vector representations (embeddings) of sentences using transformer models. It includes two approaches:

- **Manual pooling** with Hugging Face's `AutoModel` and mean pooling over token embeddings.
- **Simplified approach** using the `sentence-transformers` library, which encapsulates pooling and normalization.

The embeddings can be used for semantic similarity search, clustering, or as features for downstream tasks.

## Requirements

- Python 3.7+
- PyTorch
- Transformers (Hugging Face)
- Sentence-Transformers
- (Optional) NumPy

Install dependencies:

```bash
pip install torch transformers sentence-transformers
```

## Setup

1. **Create a virtual environment** (optional but recommended):
   ```bash
   python3 -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   ```

2. **Install the required packages** (see above).

## Usage

### Method 1: Using AutoModel with Mean Pooling

This method gives you full control over the embedding process. It loads a pre‑trained model from Hugging Face, tokenizes sentences, and applies mean pooling to obtain a single vector per sentence.

```python
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

# Example sentences
sentences = [
    'I need a backend developer with JavaScript experience',
    'I have 6 years of experience in FastAPI'
]

# Tokenize
encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

# Compute embeddings
with torch.no_grad():
    model_output = model(**encoded_input)

# Pool and normalize
sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

print('Embeddings shape:', sentence_embeddings.shape)   # (2, 384)
```

### Method 2: Using SentenceTransformer (Simpler)

The `sentence-transformers` library provides a ready‑to‑use wrapper that handles tokenization, pooling, and normalization automatically.

```python
from sentence_transformers import SentenceTransformer
import torch.nn.functional as F

# Load the model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sentences
sentences = [
    'I need a backend developer with JavaScript experience',
    'I have 6 years of experience in FastAPI'
]

# Generate embeddings (returns numpy array)
embeddings = model.encode(sentences)
print('Embeddings shape:', embeddings.shape)   # (2, 384)

# Convert to torch tensor for similarity calculation
emb1 = torch.tensor(embeddings[0])
emb2 = torch.tensor(embeddings[1])
similarity = F.cosine_similarity(emb1, emb2, dim=0)
print('Cosine similarity:', similarity.item())
```

## Cosine Similarity

Both methods produce normalized embeddings, so cosine similarity can be computed directly:

```python
similarity = F.cosine_similarity(sentence_embeddings[0], sentence_embeddings[1], dim=0)
print('Similarity score:', similarity.item())
```

## Tensor ↔ List Conversion

If you need to store embeddings or pass them to other libraries, convert between PyTorch tensors and Python lists:

```python
# Tensor to list
embedding_list = sentence_embeddings[0].tolist()
print(embedding_list[:5])   # first five values

# List back to tensor
embedding_tensor = torch.tensor(embedding_list)
```

## Example Output

```
Embeddings shape: torch.Size([2, 384])
Cosine similarity score: 0.4567
```

The exact similarity value will depend on the model and the input sentences.

## Notes

- The model `all-MiniLM-L6-v2` produces 384‑dimensional embeddings. Other models (e.g., `all-mpnet-base-v2`) give different dimensions.
- For large‑scale similarity searches, consider using libraries like FAISS or Annoy.
- The manual pooling method (Method 1) is useful if you need to modify the pooling strategy or use a model not available in `sentence-transformers`.
