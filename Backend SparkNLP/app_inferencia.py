import gc
from app_embeddings import *
from app_model import *
from app_spark_processor import *
from app_text_pprocessor import *
from torch.utils.data import DataLoader, TensorDataset
import torch.nn.functional as F
import xgboost as xgb
import sparknlp

class Inferencia():
    def __init__(self, path, type='parquet',spark=None):
        self.path = path
        self.type = type
        self.spark=spark
        self.model_paths_xbg1= [
            "./models/best_model_0.41709946827292443_.pth",
            "./models/best_model_0.4170598139226437_.pth",
            "./models/best_model_0.4178334002554417_.pth",
            "./models/best_model_0.41695730561614036_.pth",
            "./models/best_model_0.41835537834763525_.pth"
        ]
        self.model_paths = [
            './models/best_model_0.4178334002554417_.pth',
            './models/best_model_0.4338203712284565_.pth',
            './models/best_model_0.41933973712325096_.pth',
            './models/best_model_0.3818274104833603_.pth',
            './models/best_model_0.4177737632036209_.pth',
            './models/best_model_0.4170763077020645_.pth',
            './models/best_model_0.4199480821490288_.pth',
            './models/best_model_0.4171988932073116_.pth'
        ]
        datasete = DatasetLoader(spark)
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
        bert_numpy, w2v_numpy = embeddings.get_embeddings()
        
        bert_tensor = torch.tensor(bert_numpy, dtype=torch.float32)
        w2v_tensor = torch.tensor(w2v_numpy, dtype=torch.float32)
               
        dataset = TensorDataset(bert_tensor, w2v_tensor)
        loader = DataLoader(dataset, batch_size=512, shuffle=False)
        
        all_preds = []
        for path in self.model_paths:
            model = SentimentClassifierNN( w2v_dim=350,bert_dim=512,dropout_rate=0.42, fun_activation=nn.Mish()) 
            model.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
            model.eval()

            preds = []
            with torch.no_grad():
                for b, w in loader:
                    out = model(b, w)
                    prob = F.softmax(out, dim=1)
                    preds.append(prob.numpy())

            all_preds.append(np.vstack(preds))
            del model
            gc.collect()
       
        stacked_features = np.concatenate(all_preds, axis=1)

        stacking_model = xgb.XGBClassifier()
        stacking_model.load_model("./models/xgb_stacking_best_model3.json")
        final_preds = stacking_model.predict(stacked_features)
        final_probs = stacking_model.predict_proba(stacked_features).max(axis=1) * 100
        predictions_list = [
             {"predict": int(pred), "prob": f"{prob:.2f}%"} for pred, prob in zip(final_preds, final_probs)
        ]
        del (
        bert_tensor,
        w2v_tensor,
        dataset,
        loader,
        final_preds,
        final_probs,
        stacked_features,
        embeddings,
        df_spark,
        stacking_model,
       )
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return predictions_list
    