### 📝 TextCleaner - Limpieza y Normalización de Texto en Spark NLP

#### 📌 Descripción
`TextCleaner` es un pipeline de procesamiento de texto basado en **Spark NLP** que aplica varias transformaciones para limpiar, normalizar y optimizar texto en tareas de NLP.

---

#### 🔄 Proceso de Limpieza
1. **Expansión de Contracciones**  
   - Convierte contracciones a su forma extendida.  
   - Ejemplo: `"can't"` → `"cannot"`, `"I'm"` → `"I am"`.

2. **Conversión a Minúsculas**  
   - Asegura la uniformidad del texto.

3. **Tokenización**  
   - Divide el texto en tokens individuales.

4. **Filtrado de Stopwords**  
   - Elimina palabras irrelevantes para NLP, **pero conserva negaciones importantes** como:  
     `"not"`, `"cannot"`, `"never"`, `"without"`, `"don't"`, etc.

5. **Normalización de Texto**  
   - Corrige caracteres especiales, acentos y signos de puntuación.

6. **Lematización**  
   - Convierte palabras a su forma base.  
   - Ejemplo: `"running"` → `"run"`, `"better"` → `"good"`.

7. **Generación de Embeddings** *(opcional)*  
   - Puede generar representaciones vectoriales para modelos de ML/NLP.

---

#### 📥 Entrada
Un **DataFrame de Spark** con una columna de texto.

#### 📤 Salida
Un **DataFrame de Spark** con columnas adicionales:
- `document`: Representación estructurada del texto.
- `tokens`: Lista de palabras tokenizadas.
- `normalized`: Texto limpio y normalizado.
- `filtered_tokens`: Tokens sin stopwords innecesarias.
- `lemmatized`: Tokens en su forma base.

---

#### 🚀 Ejemplo de Uso
```python
cleaner = TextCleaner(spark, use_lemma=True, use_stop_words=True, expand_contractions=True)
cleaned_df = cleaner.clean_dataframe(df)
cleaned_df.select("lemmatized").show(truncate=False)
```

###  Flujo de Entrenamiento con Spark NLP y Optuna 🎯

Este documento describe el proceso de entrenamiento utilizando **Spark NLP** para la limpieza y procesamiento de datos de texto, junto con **Optuna** para la optimización de hiperparámetros en un modelo de clasificación basado en **BERT** y **TF-IDF**.

 📌 1. Inicialización del Entorno
Se inicia la sesión de **Spark NLP** para procesar datos de texto:

```python
import sparknlp
spark = sparknlp.start()
processor = SparkNLPProcessor(spark_session=spark)
spark = processor.get_session()
```

#### 📌 2. Carga y Preprocesamiento de Datos
Se carga el dataset desde un archivo CSV y se filtran los datos para incluir solo los ejemplos con `sentiment` igual a `0` o `1`. Luego, se aplica una limpieza de texto avanzada.

```python
datasete = DatasetLoader(spark)
test = datasete.load_csv('/content/drive/MyDrive/NeoNexus/train_dataset.csv')
df_filtered = test.filter(col("sentiment").isin([0, 1]))
df_ = TextCleaner(spark, use_lemma=True, use_stop_words=True, expand_contractions=True).clean_dataframe(df_filtered)
```

#### 📌 3. Carga de Representaciones de Texto
Se cargan las representaciones de texto preprocesadas con **BERT** y **TF-IDF**, junto con las etiquetas de clasificación.

```python
import numpy as np
bert_numpy = np.load("/content/drive/MyDrive/NeoNexus/bert_numpy.npy")
tfidf_numpy = np.load("/content/drive/MyDrive/NeoNexus/tfidf_features.npy")
labels = np.load("/content/drive/MyDrive/NeoNexus/labels.npy")
```

#### 📌 4. Optimización de Hiperparámetros con Optuna
Se define una clase `HyperparameterOptimization` que emplea **Optuna** para explorar combinaciones de hiperparámetros y seleccionar la mejor configuración para el modelo.

```python
study = HyperparameterOptimization(
    bert_numpy=bert_numpy,
    tfidf_numpy=tfidf_numpy,
    labels=labels
).optimize()
```

La optimización se realiza en función de:
- **Tasa de aprendizaje (`lr`)**
- **Decaimiento de peso (`weight_decay`)**
- **Dropout (`dropout`)**
- **Tamaño del batch (`batch_size`)**
- **Optimizador (`Adam`, `AdamW`, `SGD`)**

#### 📌 5. Entrenamiento del Modelo
El modelo es entrenado utilizando la mejor configuración de hiperparámetros obtenida por **Optuna**.

```python
trainer = Trainer(
    input_tfidf_dim=tfidf_numpy.shape[1],
    input_bert_dim=bert_numpy.shape[1],
    bert_numpy=bert_numpy,
    tfidf_numpy=tfidf_numpy,
    labels=labels,
    criterion=nn.CrossEntropyLoss(),
    optimizer=selected_optimizer,
    epochs=35,
    batch_size=batch_size,
    learning_rate=lr,
    weight_decay=weight_decay,
    dropout=dropout
)
val_losses = trainer.train()
```

---


