from app_embeddings import *
from app_hyperparams import HyperparameterOptimization
from app_text_pprocessor import *
import argparse,sparknlp
from app_spark_processor import *
from scipy import sparse

def getArguments():
    parse=argparse.ArgumentParser(description="Opciones de servicios")
    parse.add_argument("--services",help="[train, embeddings, cleaned]", required=True)
    parse.add_argument("--name",help="[Nombre del dataset para realizar el entrenamiento]",default='train.parquet', required=False)
    parse.add_argument("--to",help="[Nombre del dataset de salida para guardar]",default='cleaned_df_v2.parquet', required=False)
    parse.add_argument("--batch", help="Reaizar el proceso de limpieza por batch, por default is False", default=False, required=False)
    args=parse.parse_args()
    return args

def main():
    args=getArguments()
    services=args.services
    if services=='train':
        print("⏳ Cargando los embeddings.....")
        bert_numpy = np.load("./embeddings/bert_numpy.npy")
        w2v_numpy=np.load('./embeddings/w2v_numpy.npy')
        tfidf_numpy = sparse.load_npz("./embeddings/tfidf_features.npz").toarray()
        labels = np.load("./embeddings/labels.npy")
        study=HyperparameterOptimization(bert_numpy=bert_numpy,tfidf_numpy=tfidf_numpy,w2v_numpy=w2v_numpy, labels=labels)
        study.optimize()
        
    elif services=='cleaned':
        name=args.name
        to=args.to
        spark = sparknlp.start()
        processor = SparkNLPProcessor(spark_session=spark)
        spark = processor.get_session()
        datasete = DatasetLoader(spark)
        print("🧹 Estamos Procesando el Texto en estos momentos.....")
        text_cleaned=TextCleaner(spark, use_lemma=True, use_stop_words=True,expand_contractions=True)
        if args.batch:
            df_=text_cleaned.process_in_batches(f'file:///home/alexandra0822_diaz/spark-nlp-neonexus/datasets/{name}')
        else:
          train = datasete.load_parquet(f'file:///home/alexandra0822_diaz/spark-nlp-neonexus/datasets/{name}').repartition(10)  
          df_=text_cleaned.clean_dataframe(train) 
        print("✍️ Estamos escribiendo el dataframe procesado en estos momentos ....")
        df_.write.mode("overwrite").parquet(f"file:///home/alexandra0822_diaz/spark-nlp-neonexus/datasets/{to}")
        print("🚀 Hemos finalizado.")
        
    elif services=='embeddings':
       path='./datasets/cleaned_df.parquet'
       embeddings=Embeddings(path)
       if embeddings:
           print("⏳ Procesando.....")
           bert_numpy, tfidf_numpy, w2v_numpy, labels_numpy = embeddings.extract_embeddings()
           print(f"BERT Embeddings Shape: {bert_numpy.shape}")
           print(f"TF-IDF Features Shape: {tfidf_numpy.shape}")
           print(f"W2V Features Shape: {w2v_numpy.shape}")
           print(f"Labels Shape: {labels_numpy.shape}")
    else:
       print(" Opciones no reconocidas, son [train, embeddings]")
        

if __name__=='__main__':
    main()    