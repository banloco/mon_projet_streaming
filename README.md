# Crypto Real-Time Analytics Pipeline

Ce projet est un pipeline de données complet (End-to-End) permettant de traiter des flux financiers en temps réel. Il capture les prix du Bitcoin via l'API Binance, les transporte de manière résiliente avec Kafka, les analyse avec Spark Structured Streaming, et les visualise dynamiquement sur Grafana.

---

## Architecture du Système



Le pipeline est divisé en quatre couches principales :
1.  **Ingestion** : Un script Python (`crypto_producer.py`) récupère les trades via WebSocket et les publie dans **Kafka**.
2.  **Transport** : **Apache Kafka** sert de bus de messages pour découpler la source du traitement.
3.  **Traitement** : **PySpark** effectue des agrégations temporelles (Moving Average) sur des fenêtres glissantes de 30 secondes avec gestion des données tardives (**Watermarking**).
4.  **Stockage & Visualisation** : Les résultats sont persistés dans **InfluxDB** et affichés en temps réel sur **Grafana**.

---

## Stack Technique

* **Langage** : Python 3.9+
* **Flux de messages** : Apache Kafka (Confluent Platform)
* **Traitement réparti** : Apache Spark 3.5.0
* **Base de données Time-Series** : InfluxDB 2.7
* **Monitoring** : Grafana
* **Containerisation** : Docker & Docker Compose

---

## Installation et Utilisation

### 1. Cloner le projet et lancer l'infrastructure
```bash
git clone 
cd crypto-streaming-pipeline
docker compose -f infra/docker-compose.yml up -d
```

### 2. Lancer le Producer (Capture des données)
Dans un premier terminal (environnement local) :
```bash
pip install confluent-kafka websocket-client
python producers/crypto_producer.py
```

### 3. Lancer le Stream Processor (Calcul Spark)
Dans un second terminal :
```bash
# Installation du client InfluxDB dans le conteneur Spark
docker exec -u 0 -it infra-spark-master-1 pip install influxdb-client

# Soumission du job Spark
docker exec -u 0 -it infra-spark-master-1 /opt/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  /opt/spark/spark_jobs/stream_processor.py
```

# Visualisation des Résultats

Accédez au dashboard Grafana via http://localhost:3000 (admin/admin).

Requête Flux utilisée pour le graphique :
Extrait de code

from(bucket: "crypto")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "crypto_avg")
  |> filter(fn: (r) => r["_field"] == "average_price")
  |> yield(name: "BTC_Price_Trend")

# Concepts Data Engineering Appliqués

Windowing : Agrégation de données par fenêtres temporelles de 30 secondes.

Watermarking : Gestion des données arrivant avec un retard (seuil de 1 minute) pour garantir l'intégrité de la mémoire vive de Spark.

Checkpointing : (Optionnel) Sauvegarde de l'état du stream pour la reprise après panne.

Network Isolation : Configuration des listeners Kafka pour la communication inter-conteneurs Docker.

# Auteur

banloco - Passionné par le Big Data et le Streaming Analytics.
