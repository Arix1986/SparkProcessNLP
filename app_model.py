import torch.nn as nn
import torch

class SentimentClassifierNN(nn.Module):
    def __init__(self, tfidf_dim, bert_dim=768, dropout_rate=0.3):
        super(SentimentClassifierNN, self).__init__()

       
        self.bert_fc = nn.Linear(bert_dim, 128)
        self.bert_bn = nn.BatchNorm1d(128)  
        self.bert_dropout = nn.Dropout(dropout_rate)  

      
        self.tfidf_fc = nn.Linear(tfidf_dim, 128)
        self.tfidf_bn = nn.BatchNorm1d(128) 
        self.tfidf_dropout = nn.Dropout(dropout_rate)  

        
        self.combined_fc = nn.Linear(256, 64)
        self.combined_bn = nn.BatchNorm1d(64) 
        self.combined_dropout = nn.Dropout(dropout_rate)

       
        self.output = nn.Linear(64, 3)  # (Positivo, Negativo, Neutral)

       
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, bert_embeddings, tfidf_features):
        
        bert_out = self.relu(self.bert_fc(bert_embeddings))
        bert_out = self.bert_bn(bert_out)
        bert_out = self.bert_dropout(bert_out)

       
        tfidf_out = self.relu(self.tfidf_fc(tfidf_features))
        tfidf_out = self.tfidf_bn(tfidf_out)
        tfidf_out = self.tfidf_dropout(tfidf_out)

       
        combined = torch.cat((bert_out, tfidf_out), dim=1)
        combined_out = self.relu(self.combined_fc(combined))
        combined_out = self.combined_bn(combined_out)
        combined_out = self.combined_dropout(combined_out)

        return self.softmax(self.output(combined_out))

