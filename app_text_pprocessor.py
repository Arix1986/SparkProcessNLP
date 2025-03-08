
from sparknlp.base import DocumentAssembler
from sparknlp.annotator import Tokenizer, Normalizer,StopWordsCleaner, LemmatizerModel,BertSentenceEmbeddings
from pyspark.ml.feature import HashingTF, IDF
from pyspark.ml import Pipeline
from pyspark.sql.functions import udf, col
from pyspark.sql.types import ArrayType,StringType
import json
import re




class TextCleaner:
    def __init__(self, spark, use_lemma=True, use_stop_words=True, expand_contractions=True):
        self.spark = spark
        self.use_lemma = use_lemma
        self.use_stop_words = use_stop_words
        self.exp_contractions = expand_contractions
        self.num_features = 5000

        with open("/content/drive/MyDrive/NeoNexus/contractions.json", "r") as file:
            contractions_dict = json.load(file)

        default_stopwords = StopWordsCleaner.loadDefaultStopWords("english")
        words_to_keep = {
            "not", "no", "never", "none", "nobody", "nowhere", "nothing", "neither", "nor",
            "cannot", "without", "do not", "does not", "did not", "is not", "are not",
            "was not", "were not", "has not", "have not", "had not", "should not",
            "would not", "must not", "might not", "could not", "need not", "but", "should not", "if"
        }
        filtered_stopwords = list(set(default_stopwords) - words_to_keep)

        contractions_broadcast = self.spark.sparkContext.broadcast(contractions_dict)
        broadcast_value = contractions_broadcast.value
        expand_bool = self.exp_contractions

        self.text_cleaning_udf = udf(lambda text: TextCleaner.clean_text(text, broadcast_value, expand_bool), StringType())

        self.document_assembler = DocumentAssembler() \
            .setInputCol("reviewText") \
            .setOutputCol("document")

        self.tokenizer = Tokenizer() \
            .setInputCols(["document"]) \
            .setOutputCol("tokens")

        self.normalizer = Normalizer() \
            .setInputCols(["tokens"]) \
            .setOutputCol("normalized") \
            .setLowercase(True)

        if use_stop_words:
            self.stopwords_cleaner = StopWordsCleaner() \
                .setInputCols(["normalized"]) \
                .setOutputCol("filtered_tokens") \
                .setStopWords(filtered_stopwords) \
                .setCaseSensitive(False)
            stopwords_output = "filtered_tokens"
        else:
            stopwords_output = "normalized"

        self.model_dir = "./models/lemma_antbnc"

        if use_lemma:
            self.lemmatizer = LemmatizerModel.load(self.model_dir) \
                .setInputCols([stopwords_output]) \
                .setOutputCol("lemmatized")
            lemma_output = "lemmatized"
        else:
            lemma_output = stopwords_output

        self.bert_embedder = BertSentenceEmbeddings.pretrained("sent_small_bert_L2_128", "en") \
            .setInputCols(["document"]) \
            .setOutputCol("bert_embeddings")

        self.extract_lemma_udf = udf(lambda x: [token.result for token in x] if x else [], ArrayType(StringType()))

        self.vector_tfidf = HashingTF(inputCol="lemmas_array", outputCol="raw_features", numFeatures=self.num_features)
        self.idf = IDF(inputCol="raw_features", outputCol="tfidf_features")
        

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

    def clean_dataframe(self, df):
        df = df.withColumn("reviewText", self.text_cleaning_udf(df["reviewText"]))
        self.pipeline = Pipeline(stages=[
            self.document_assembler,
            self.tokenizer,
            self.normalizer,
            self.stopwords_cleaner if self.use_stop_words else None,
            self.lemmatizer if self.use_lemma else None,
            self.bert_embedder
        ])
        df=self.pipeline.fit(df).transform(df)
        df = df.withColumn("lemmas_array", col("lemmatized").getItem("result"))
        self.vector_tfidf = HashingTF(inputCol="lemmas_array", outputCol="raw_features", numFeatures=self.num_features)
        self.idf = IDF(inputCol="raw_features", outputCol="tfidf_features")
        self.pipeline_tfidf = Pipeline(stages=[self.vector_tfidf, self.idf])
        return self.pipeline_tfidf.fit(df).transform(df)