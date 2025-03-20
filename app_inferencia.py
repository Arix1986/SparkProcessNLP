from app_embeddings import *
from app_model import *
from app_spark_processor import *
from app_text_pprocessor import *
from torch.utils.data import DataLoader, TensorDataset
import torch.nn.functional as F
import sparknlp

class Inferencia():
    def __init__(self, path, type='parquet'):
        self.path = path
        self.type = type
        self.spark = sparknlp.start()
        processor = SparkNLPProcessor(spark_session=self.spark)
        self.spark = processor.get_session()
        datasete = DatasetLoader(self.spark)
        if type=='parquet':
            try:
               self.df = datasete.load_parquet(path)
            except Exception as e:
                print(f"Error al cargar el archivo {e}")
        elif type=='csv':
            try:
              self.df = datasete.load_csv(path)
            except Exception as e:
                print(f"Error al cargar el archivo {e}")  
        else:
            raise ValueError("Tipo de archivo no reconocido")        

    def predecir(self):
       
        df_spark=TextCleaner(self.spark,expand_contractions=True).clean_dataframe(self.df)
        embeddings=Embeddings(df_spark)     
        bert_numpy, w2v_numpy, labels_numpy = embeddings.get_embeddings()
        
        bert_tensor = torch.tensor(bert_numpy, dtype=torch.float32)
        w2v_tensor = torch.tensor(w2v_numpy, dtype=torch.float32)
        label_tensor = torch.tensor(labels_numpy, dtype=torch.long)
        
        test_dataset = TensorDataset(bert_tensor, w2v_tensor, label_tensor)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        model_path="./models/best_model_0.42315637332201006_.pth"
        model = SentimentClassifierNN(bert_dim=512, w2v_dim=350, activation_function=nn.GELU())
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        predictions_list = []
        with torch.no_grad():
            for bert_features, w2v_features in test_loader:
                outputs = model(bert_features, w2v_features)
             
                probs = F.softmax(outputs, dim=1)
                predictions = probs.argmax(dim=1).cpu().numpy()
                probabilities = probs.max(dim=1).values.cpu().numpy() * 100  
             
                predictions_list.extend([
                    {"predict": int(pred), "prob": f"{prob:.2f}%"} for pred, prob in zip(predictions, probabilities)
                ])
        return predictions_list
    
    