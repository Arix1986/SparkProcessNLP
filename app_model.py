import torch.nn as nn
import torch

class SentimentClassifierNN(nn.Module):
    def __init__(self, w2v_dim=350, bert_dim=512, dropout_rate=0.3, fun_activation=nn.GELU(), num_classes=2):
        super(SentimentClassifierNN, self).__init__()
        hidden_dim=128
        
        self.bert_fc = nn.Linear(bert_dim, hidden_dim)
        self.bert_bn = nn.BatchNorm1d(hidden_dim, momentum=0.1)
        self.bert_dropout = nn.Dropout(dropout_rate)

        
        self.w2v_fc = nn.Linear(w2v_dim, hidden_dim)
        self.w2v_bn = nn.BatchNorm1d(hidden_dim, momentum=0.1)
        self.w2v_dropout = nn.Dropout(dropout_rate)

        
        combined_dim = hidden_dim * 2
        self.combined_fc = nn.Linear(combined_dim, hidden_dim)
        self.combined_bn = nn.BatchNorm1d(hidden_dim, momentum=0.1)
        self.combined_dropout = nn.Dropout(dropout_rate)

        
        self.output = nn.Linear(hidden_dim, num_classes)

       
        self.fun_activation = fun_activation

    def forward(self, bert_embeddings, w2v_features):
       
        bert_out = self.bert_fc(bert_embeddings)
        bert_out = self.bert_bn(bert_out)
        bert_out = self.fun_activation(bert_out)
        bert_out = self.bert_dropout(bert_out)

        
        w2v_out = self.w2v_fc(w2v_features)
        w2v_out = self.w2v_bn(w2v_out)
        w2v_out = self.fun_activation(w2v_out)
        w2v_out = self.w2v_dropout(w2v_out)

       
        combined = torch.cat((bert_out, w2v_out), dim=1)
        combined_out = self.combined_fc(combined)
        combined_out = self.combined_bn(combined_out)
        combined_out = self.fun_activation(combined_out)
        combined_out = self.combined_dropout(combined_out)

        return self.output(combined_out)

