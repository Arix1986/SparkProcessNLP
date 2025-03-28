from pyspark.sql import SparkSession
import sparknlp


class SparkNLPProcessor:
    def __init__(self, app_name="Spark NLP Processor", spark_session=None):
        if spark_session:
            self.spark = spark_session
        else:
            self.spark = SparkSession.builder \
                .appName(app_name) \
                .config("spark.driver.memory", "16g") \
                .config("spark.executor.memory", "16g") \
                .config("spark.kryoserializer.buffer.max", "1500M") \
                .config("spark.rpc.message.maxSize", "256") \
                .getOrCreate()
            sparknlp.start(spark=self.spark)
            print(f"Spark NLP versión: {sparknlp.version()}")


    def get_session(self):
        return self.spark

class DatasetLoader:
    def __init__(self, spark_session):
        self.spark = spark_session

    def load_csv(self, file_path, header=True, infer_schema=True):
        return self.spark.read.csv(file_path, header=header, inferSchema=infer_schema)

    def load_parquet(self, file_path):
        return self.spark.read.parquet(file_path)