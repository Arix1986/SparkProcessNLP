from pyspark.sql import SparkSession
import sparknlp


class SparkNLPProcessor:
    def __init__(self, app_name="Spark NLP Processor", spark_session=None):
        if spark_session:
            self.spark = spark_session
        else:
            self.spark = SparkSession.builder \
                .appName("SparkNLP") \
                .master("local[*]") \
                .config("spark.jars", "/app/jars/spark-nlp-assembly-5.5.3.jar") \
                .getOrCreate()
            sparknlp.start(spark=self.spark)
            print(f"Spark NLP versión: {sparknlp.version()}")


    def get_session(self):
        return self.spark

class DatasetLoader:
    def __init__(self, spark_session):
        self.spark = spark_session

    def load_csv(self, file_path, header=True, infer_schema=True):
        return self.spark.read.option("header", header) \
                           .option("inferSchema", infer_schema) \
                           .option("multiLine", True) \
                           .option("escape", '"') \
                           .csv(file_path)

    def load_parquet(self, file_path):
        return self.spark.read.parquet(file_path)