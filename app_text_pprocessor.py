import os
import numpy as np
import pandas as pd
from sparknlp.base import DocumentAssembler 
from sparknlp.annotator import Tokenizer, Normalizer,BertSentenceEmbeddings,Word2VecApproach
from pyspark.ml import Pipeline, PipelineModel
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import json
import re


class TextCleaner:
    def __init__(self, spark,expand_contractions=True):
        self.spark = spark
        self.exp_contractions = expand_contractions
        

        with open("./contractions.json", "r") as file:
            contractions_dict = json.load(file)

        contractions_broadcast = self.spark.sparkContext.broadcast(contractions_dict)
        broadcast_value = contractions_broadcast.value
        expand_bool = self.exp_contractions

        self.text_cleaning_udf = udf(lambda text: TextCleaner.clean_text(text, broadcast_value, expand_bool), StringType())

        self.document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document") \
            .setCleanupMode("shrink")

        self.tokenizer = Tokenizer() \
            .setInputCols(["document"]) \
            .setOutputCol("tokens")

        self.normalizer = Normalizer() \
            .setInputCols(["tokens"]) \
            .setOutputCol("normalized") \
            .setLowercase(True)
        

        self.model_dir = "./models/lemma_antbnc"

        self.bert_embedder = BertSentenceEmbeddings.pretrained("sent_small_bert_L8_512", "en") \
            .setInputCols(["document"]) \
            .setOutputCol("bert_embeddings") \
            .setMaxSentenceLength(128)

        self.pipelin_general_path = "./models/w2v/pipelines/pipeline_general"
        self.pipelin_w2v_path = "./models/w2v/pipelines/pipeline_w2v"
               
        self.word2vec = Word2VecApproach() \
            .setInputCols(["normalized"]) \
            .setOutputCol("word2vec_embeddings") \
            .setVectorSize(350) \
            .setMinCount(4) \
            .setWindowSize(6) \
            .setMaxIter(15) \
            .setStepSize(0.025 ) \
            .setMaxSentenceLength(1000) \
            .setSeed(42)


    @staticmethod
    def clean_text(text, contractions_dict, expand_contractions):
        if not text:
            return "UNK"
        if expand_contractions:
            for contraction, expanded in contractions_dict.items():
                text = re.sub(r'\b' + re.escape(contraction) + r'\b', expanded, text)
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"\S+@\S+\.\S+", "", text)
        text = re.sub(r"\d+", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        text = text.strip()
        return text if text else "UNK"

    def model_exists(self,path):
      return os.path.exists(path)

    def clean_dataframe(self, df):
      print("🚀 Iniciando proceso de limpieza de datos...")
      df = df.withColumn("text", self.text_cleaning_udf(df["text"]))
      if self.model_exists(self.pipelin_general_path):
          pipeline_general = PipelineModel.load(self.pipelin_general_path)
      else:
          self.pipeline = Pipeline(stages=[
            self.document_assembler,
            self.tokenizer,
            self.normalizer,
            self.bert_embedder,
           ])
          pipeline_stages = self.pipeline.getStages() 
          pipeline_stages = [stage for stage in pipeline_stages if stage is not None]
          pipeline_general = self.pipeline.fit(df)
          pipeline_general.write().overwrite().save(self.pipelin_general_path)
      print("🚀 Iniciando Pipeline General...")
      df= pipeline_general.transform(df)
      print("🚀 Iniciando Pipeline Word2Vec...")
      
   
      if self.model_exists(self.pipelin_w2v_path):
          pipeline_w2v = PipelineModel.load(self.pipelin_w2v_path)
      else:
          pipeline_w2v = Pipeline(stages=[
              self.word2vec
          ])
          pipeline_w2v = pipeline_w2v.fit(df)
          pipeline_w2v.write().overwrite().save(self.pipelin_w2v_path)

      df = pipeline_w2v.transform(df)
      return df