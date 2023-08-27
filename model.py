from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

class SentenceEmbeddingModel(torch.nn.Module):
    def __init__(self, model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1",device="cuda"):
        super(SentenceEmbeddingModel, self).__init__()
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = torch.jit.load("embeds.pt").to(device)

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode(self, texts):
        # Tokenize sentences
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(self.device)

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(encoded_input["input_ids"],encoded_input['attention_mask'])

        # Perform pooling
        embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings
    def forward(self,query, docs):
      query_emb = F.normalize(self.mean_pooling(self.model(query['input_ids'],query['attention_mask']),query['attention_mask']), p=2, dim=1)
      doc_emb = F.normalize(self.mean_pooling(self.model(docs["input_ids"],docs["attention_mask"]),docs['attention_mask']), p=2, dim=1)
      scores = torch.mm(query_emb, doc_emb.transpose(0, 1))
      return scores

    def predict(self, query, docs):
        query_emb = self.encode(query)
        doc_emb = self.encode(docs)

        # Compute dot score between query and all document embeddings
        scores = torch.mm(query_emb, doc_emb.transpose(0, 1))[0]

        return scores
