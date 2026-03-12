from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F


# --------------------
# Generate Embeddings
# --------------------
#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

# Sentences we want sentence embeddings for
sentences = ['I need a backend developer with JavaScript experience', 'I have 6 years of experience in FastAPI']

# Tokenize sentences
encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

# Compute token embeddings
with torch.no_grad():
    model_output = model(**encoded_input)

# Perform pooling
sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

# Normalize embeddings
sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
print('Embeddings:', sentence_embeddings.shape)

# Cosine Similarity
similarity_score = F.cosine_similarity(sentence_embeddings[0], sentence_embeddings[1], dim=0)
print('Cosine Similarity Score:', similarity_score)

# -------------------
# Alternative Way
# -------------------

# # Download and initialize the model
# model_name = "all-MiniLM-L6-v2"
# embedder = SentenceTransformer(model_name)

# # Generate embeddings
# sentences = ['I need a backend developer with JavaScript experience', 'I have 6 years of experience in FastAPI']
# sentence_embeddings = embedder.encode(sentences)

# print('Embeddings shape:')
# print(embeddings.shape) # These embeddings has the type numpy.ndarray

# # Calculate the similarity
# similarity_score = F.cosine_similarity(torch.tensor(sentence_embeddings[0]), torch.tensor(sentence_embeddings[1]), dim=0)

# print('Similarity Score:')
# print(similarity_score)

# -------------------
# Tensor <=> List (Conversion)
# -------------------

# Convert a tensor to list
embeddings_arr = sentence_embeddings[0].tolist()
print(embeddings_arr[:10])

# Convert the list into the tensor
embeddings = torch.tensor(embeddings_arr)
print(embeddings[:10])