
from sparknlp.base import DocumentAssembler
from sparknlp.annotator import Tokenizer, Normalizer,StopWordsCleaner, LemmatizerModel,BertSentenceEmbeddings
from pyspark.ml.feature import HashingTF, IDF
from pyspark.ml import Pipeline
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import json
import re




class TextCleaner:
   
    def __init__(self, spark, use_lemma=True, use_stop_words=True,expand_contractions=True):
        self.spark = spark
        self.use_lemma = use_lemma
        self.use_stop_words = use_stop_words
        self.exp_contractions=expand_contractions
        with open("contractions.json", "r") as file:
             contractions_dict=json.load(file)
        
        default_stopwords = StopWordsCleaner.loadDefaultStopWords("english")
        words_to_keep = {
            "not", "no", "never", "none", "nobody", "nowhere", "nothing", "neither", "nor",
            "cannot", "without", "do not", "does not", "did not", "is not", "are not",
            "was not", "were not", "has not", "have not", "had not", "should not",
            "would not", "must not", "might not", "could not", "need not","but", "should not","if"
        }
        filtered_stopwords = list(set(default_stopwords) - words_to_keep)     
             
           
        contractions_broadcast = self.spark.sparkContext.broadcast(contractions_dict)
        broadcast_value = contractions_broadcast.value  
        expand_bool = self.exp_contractions
        
        self.text_cleaning_udf = udf(lambda text: TextCleaner.clean_text(text, broadcast_value, expand_bool), StringType())
        
        self.document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")

        self.tokenizer = Tokenizer() \
            .setInputCols(["document"]) \
            .setOutputCol("tokens")

        self.normalizer = Normalizer() \
            .setInputCols(["tokens"]) \
            .setOutputCol("normalized") \
            .setLowercase(True)
            
        self.stopwords_cleaner = StopWordsCleaner() \
            .setInputCols(["normalized"]) \
            .setOutputCol("filtered_tokens") \
            .setStopWords(filtered_stopwords) \
            .setCaseSensitive(False) if use_stop_words else None
            
        self.model_dir = "models/lemma_antbnc"
         

        self.lemmatizer = LemmatizerModel.load(self.model_dir) \
            .setInputCols(["filtered_tokens" if use_stop_words else "normalized"]) \
            .setOutputCol("lemmatized") if use_lemma else None    
        
        self.bert_embedder  = BertSentenceEmbeddings.pretrained("distilbert_base_uncased", "en") \
            .setInputCols(["document"]) \
            .setOutputCol("bert_embeddings")
        
        self.vector_tfidf = HashingTF(inputCol="lemmatized", outputCol="raw_features", numFeatures=self.num_features)
        self.idf = IDF(inputCol="raw_features", outputCol="tfidf_features")    
            
        stages = [self.document_assembler, self.tokenizer, self.normalizer]

        if use_stop_words:
            stages.append(self.stopwords_cleaner)
        if use_lemma:
            stages.append(self.lemmatizer)
            
        stages.append(self.vector_tfidf)
        stages.append(self.idf)
        stages.append(self.bert_embedder)
        
        self.pipeline = Pipeline(stages=stages)    

    @staticmethod
    def clean_text(text,contractions_dict, expand_contractions):
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
    
    def clean_dataframe(self, df):
        df = df.withColumn("text", self.text_cleaning_udf(df["text"]))
        return self.pipeline.fit(df).transform(df)