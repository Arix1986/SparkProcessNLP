import pandas as pd
import numpy as np


class Embeddings():
    def __init__(self, df_spark):
        self.df_pandas = df_spark.select(
            "bert_embeddings","word2vec_embeddings"
        ).toPandas()
        

    def extract_embeddings(self,row):
        embeddings = row['bert_embeddings']
        if embeddings and 'embeddings' in embeddings[0]:
            try:
                return np.array(embeddings[0]['embeddings'], dtype=np.float32)
            except (TypeError, ValueError):
                return None
        else:
            return None
    def get_w2v_embedding(self,word_embeddings):
        embeddings = [w["embeddings"] for w in word_embeddings]
        return np.mean(embeddings, axis=0) if embeddings else np.zeros(350)    

    def get_embeddings(self):
        df_bert_embeddings = self.df_pandas[['bert_embeddings']].copy()
        df_bert_embeddings['bert_embeddings_numpy'] = df_bert_embeddings.apply(lambda row: self.extract_embeddings(row), axis=1)
        bert_numpy = np.vstack(df_bert_embeddings["bert_embeddings_numpy"].to_list())
        df_w2v_embeddings=self.df_pandas[['word2vec_embeddings']].copy()
        df_w2v_embeddings['sentence_embedding'] = df_w2v_embeddings.apply(lambda row : self.get_w2v_embedding(row['word2vec_embeddings']), axis=1) 
        w2v_numpy = np.vstack(df_w2v_embeddings["sentence_embedding"].to_list())
        return bert_numpy,  w2v_numpy
    
class EmbeddingsTrainner():
    def __init__(self, df_spark):
        self.df_pandas = df_spark.select(
            "bert_embeddings","word2vec_embeddings","sentiment"
        ).toPandas()
        

    def extract_embeddings(self,row):
        embeddings = row['bert_embeddings']
        if embeddings and 'embeddings' in embeddings[0]:
            try:
                return np.array(embeddings[0]['embeddings'], dtype=np.float32)
            except (TypeError, ValueError):
                return None
        else:
            return None
    def get_w2v_embedding(self,word_embeddings):
        embeddings = [w["embeddings"] for w in word_embeddings]
        return np.mean(embeddings, axis=0) if embeddings else np.zeros(350)    

    def get_embeddings(self):
        df_bert_embeddings = self.df_pandas[['bert_embeddings']].copy()
        df_bert_embeddings['bert_embeddings_numpy'] = df_bert_embeddings.apply(lambda row: self.extract_embeddings(row), axis=1)
        bert_numpy = np.vstack(df_bert_embeddings["bert_embeddings_numpy"].to_list())
        df_w2v_embeddings=self.df_pandas[['word2vec_embeddings']].copy()
        df_w2v_embeddings['sentence_embedding'] = df_w2v_embeddings.apply(lambda row : self.get_w2v_embedding(row['word2vec_embeddings']), axis=1) 
        w2v_numpy = np.vstack(df_w2v_embeddings["sentence_embedding"].to_list())
        label= self.df_pandas['sentiment'].to_numpy()
        return bert_numpy,  w2v_numpy , label    