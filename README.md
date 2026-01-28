# Crypto Real‑Time Analytics Pipeline

## Objectif
Pipeline temps réel pour capter le prix du BTC via Binance, transporter les messages avec Kafka, calculer des moyennes mobiles avec Spark Structured Streaming et visualiser les résultats dans Grafana via InfluxDB.

## Architecture
1. **Ingestion** : [producers/crypto_producer.py](producers/crypto_producer.py) récupère les trades via WebSocket et publie dans Kafka (topic crypto-prices).
2. **Traitement** : [spark_jobs/stream_processor.py](spark_jobs/stream_processor.py) agrège sur fenêtres de 30 s avec watermark (1 min).
3. **Stockage** : InfluxDB reçoit les points average_price.
4. **Visualisation** : Grafana affiche les tendances en temps réel.

## Stack
- Python 3.9+
- Apache Kafka (Confluent)
- Spark 3.5.0
- InfluxDB 2.7
- Grafana
- Docker & Docker Compose

## Démarrage rapide
### 1) Lancer l’infrastructure
```bash
docker compose -f infra/docker-compose.yml up -d
```

### 2) Installer les dépendances locales
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Lancer le producer
```bash
python producers/crypto_producer.py
```

### 4) Lancer le job Spark
```bash
docker exec -u 0 -it infra-spark-master-1 pip install influxdb-client
docker exec -u 0 -it infra-spark-master-1 /opt/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  /opt/spark/spark_jobs/stream_processor.py
```

## Visualisation
- Grafana : http://localhost:3000 (admin/admin)
- Control Center Kafka : http://localhost:9021

## Structure du projet
```
├── infra/                     # Docker Compose (Kafka, Spark, InfluxDB, Grafana)
├── producers/                 # Producer WebSocket Binance
├── spark_jobs/                # Job Spark Structured Streaming
├── notebooks/                 # Notebooks d’analyse
├── requirements.txt
└── README.md
```
