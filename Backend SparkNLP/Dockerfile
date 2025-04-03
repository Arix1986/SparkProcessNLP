FROM python:3.9-slim

RUN apt-get update && apt-get install -y openjdk-17-jdk-headless && \
    apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/jars && \
    curl -L -o /app/jars/spark-nlp-assembly-5.5.3.jar https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/spark-nlp/spark-nlp-assembly-5.5.3.jar

COPY . .


EXPOSE 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]