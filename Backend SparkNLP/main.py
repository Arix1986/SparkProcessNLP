from fastapi import FastAPI, UploadFile, File, Request
from pydantic import BaseModel
import sparknlp
from pyspark.sql import SparkSession
from app_inferencia import *
from app_spark_processor import *
import functools
from fastapi.responses import JSONResponse
import gc,os

class TextInput(BaseModel):
    path: str
    tipo: str


app = FastAPI()
spark = sparknlp.start()
processor = SparkNLPProcessor(spark_session=spark)
spark = processor.get_session()

def limpiar_memoria(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        try:
            spark.catalog.clearCache()
        except Exception:
            pass

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return result

    return wrapper

@app.post("/inferencia")
@limpiar_memoria
def infer_text(data: TextInput):
    try:
        preduction=Inferencia(data.path, data.tipo,spark)
        result=preduction.predecir()
        return result
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    

@app.post("/get_test_file")
async def get_test_file(file: UploadFile = File(...)):
    try:
        os.makedirs("./datasets", exist_ok=True)
        file_path = f"./datasets/{file.filename}"

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {
            "status": "ok",
            "path": file_path,
            "type": file.content_type
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})    