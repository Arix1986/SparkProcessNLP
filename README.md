### 📝 TextCleaner - Limpieza y Normalización de Texto en Spark NLP

#### 📌 Descripción
`TextCleaner (app_text_pprocessor.py)` es una clase que implementa un pipeline de procesamiento de texto basado en **Spark NLP** que aplica varias transformaciones para limpiar, normalizar y optimizar texto en tareas de NLP.

`Embeddings & EmbeddingsTrainner (app_embeddings.py)` son clases cuya responsabilidad es dado un spark dataframe retornar los embeddings **bert_numpy**, **w2c_numpy** y **labels** en dependencia si es para inferencia o para entrenamiento.

`SentimentClassifierNN (app_model.py)` es la clase encargada de realizar la clasificación de sentimiento a partir de los embeddings generados por BERT y Word2Vec. Su arquitectura combina ambos vectores de entrada, aplica capas de normalización, activación y dropout para mejorar la generalización del modelo y finalmente genera una predicción de sentimiento en dos clases.

`SparkNLPProcessor & DatasetLoader (app_spark_processor.py) ` SparkNLPProcessor gestiona la inicialización de Spark con configuraciones optimizadas para NLP, asegurando el uso eficiente de memoria y compatibilidad con SparkNLP. DatasetLoader facilita la carga de datos en Spark, permitiendo leer archivos CSV y Parquet de forma eficiente.

`Trainer (app_training.py)` es la clase encargada del entrenamiento de la red neuronal SentimentClassifierNN, utilizando embeddings de BERT y Word2Vec. Implementa entrenamiento supervisado con PyTorch, optimización con AdamW o SGD, y evalúa el modelo en datos de validación. Incorpora early stopping basado en la pérdida de validación.

`HyperparameterOptimization (app_hyperparams.py)` es la clase que tiene la responsabilifdad de realizar la optimización de hiperparámetros para SentimentClassifierNN usando Optuna. Explora combinaciones de parámetros como la tasa de aprendizaje, función de activación, optimizador y dropout, con el objetivo de minimizar la pérdida de validación.

`Inferencia (app_inferencia.py)` es la clase que orqueta las funcionalidades de las clases anteriores y organiza el flujo desde la **carga de datos, limpieza y predicción** utilizando un modelo de clasificación de sentimientos previamente entrenado.

 **Flujo de trabajo**
1. **Carga datos (`Parquet` o `CSV`)** en Spark mediante `DatasetLoader`.  
2. **Limpia el texto con `TextCleaner`** y genera **embeddings de BERT y Word2Vec**.  
3. **Convierte los embeddings en tensores** para inferencia con PyTorch.  
4. **Carga el modelo `SentimentClassifierNN` entrenado**, realiza predicciones y aplica `softmax` para calcular probabilidades.  
5. **Retorna una lista de predicciones** en formato:
   ```json
   [
       {"predict": 1, "prob": "92.45%"},
       {"predict": 0, "prob": "85.30%"}
   ]
---

#### 🔄 Proceso de Limpieza
1. **Expansión de Contracciones**  
   - Convierte contracciones a su forma extendida.  
   - Ejemplo: `"can't"` → `"cannot"`, `"I'm"` → `"I am"`.

2. **Conversión a Minúsculas**  
   - Asegura la uniformidad del texto.

3. **Tokenización**  
   - Divide el texto en tokens individuales.


5. **Normalización de Texto**  
   - Corrige caracteres especiales, acentos y signos de puntuación.


7. **Generación de Embeddings** 
   - Se generan los Embeddings Bert de la clase sent_small_bert_L8_512 y Word2VecApproach

---

#### 📥 Entrada
Un **DataFrame de Spark** con una columna de texto.

#### 📤 Salida
Un **DataFrame de Spark** con columnas adicionales:
- `document`: Representación estructurada del texto.
- `tokens`: Lista de palabras tokenizadas.
- `normalized`: Texto limpio y normalizado.
- `bert_embeddings`: Vetor para el modelo.
- `word2vec_embeddings`: Vector para el modelo.

---

#### 🚀 Ejemplo de Uso
```python
cleaner = TextCleaner(spark, expand_contractions=True)
cleaned_df = cleaner.clean_dataframe(df)

```

###  Flujo de Entrenamiento con Spark NLP y Optuna 🎯

Este documento describe el proceso de entrenamiento utilizando **Spark NLP** para la limpieza y procesamiento de datos de texto, junto con **Optuna** para la optimización de hiperparámetros en un modelo de clasificación basado en **BERT** y **Word2VecApproach**.

 📌 1. Inicialización del Entorno
Se inicia la sesión de **Spark NLP** para procesar datos de texto:

```python
import sparknlp
spark = sparknlp.start()
processor = SparkNLPProcessor(spark_session=spark)
spark = processor.get_session()
```

#### 📌 2. Carga y Preprocesamiento de Datos
Se carga el dataset desde un archivo CSV o PARQUET y se filtran los datos para incluir solo los ejemplos con `sentiment` igual a `0` o `1`. Luego, se aplica una limpieza de texto avanzada.

```python
datasete = DatasetLoader(spark)
test = datasete.load_csv('./datasets/train_dataset.parquet')
df_ = TextCleaner(spark, use_lemma=True, use_stop_words=True, expand_contractions=True).clean_dataframe(test)
```

#### 📌 3. Carga de Representaciones de Texto
Se cargan las representaciones de texto preprocesadas con **BERT** y **Word2VecApproach**, junto con las etiquetas de clasificación.

```python
import numpy as np
bert_numpy = np.load("./embeddings/bert_numpy.npy")
w2v_numpy = np.load("./embeddings/w2v_numpy.npy")
labels = np.load("./embeddings/labels_numpy.npy")
```

#### 📌 4. Optimización de Hiperparámetros con Optuna
Se define una clase `HyperparameterOptimization` que emplea **Optuna** para explorar combinaciones de hiperparámetros y seleccionar la mejor configuración para el modelo.

```python
study = HyperparameterOptimization(
    bert_numpy=bert_numpy,
    w2v_numpy=w2v_numpy,
    labels=labels
).optimize()
```

La optimización se realiza en función de:
- **Tasa de aprendizaje (`lr`)**
- **Decaimiento de peso (`weight_decay`)**
- **Dropout (`dropout`)**
- **Tamaño del batch (`batch_size`)**
- **Optimizador (`AdamW`, `SGD`)**
-**Funciones de Activación** (`GeLU`, `SiLU`,`PReLU`,`Mish`)

#### 📌 5. Entrenamiento del Modelo
El modelo es entrenado utilizando la mejor configuración de hiperparámetros obtenida por **Optuna**.

```python
trainer = Trainer(
    input_bert_dim=bert_numpy.shape[1],
     w2v_dim=w2v_numpy.shape[1],
    bert_numpy=bert_numpy,
    w2v_numpy=w2v_numpy,
    labels=labels,
    criterion=nn.CrossEntropyLoss(),
    fun_activation=func_actication,
    optimizer=selected_optimizer,
    epochs=35,
    batch_size=batch_size,
    learning_rate=lr,
    weight_decay=weight_decay,
    dropout=dropout
)
trainer.train()
```
#### 📌 5. Inferencias del Modelo



---


