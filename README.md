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
