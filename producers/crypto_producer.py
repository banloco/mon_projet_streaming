import websocket
import json
from confluent_kafka import Producer

# Configuration pour se connecter au container Kafka
# On utilise localhost:9092 car le script tourne "hors" de Docker sur ton Linux
config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(config)


def delivery_report(err, msg):
    """ Callback appelé une fois que le message est bien reçu par Kafka """
    if err is not None:
        print(f"❌ Échec de l'envoi : {err}")
    else:
        print(f"✅ Message envoyé à {msg.topic()} [Prix: {msg.value().decode('utf-8')}]")


def on_message(ws, message):
    """ Fonction appelée à chaque fois que Binance envoie un nouveau prix """
    data = json.loads(message)

    # Extraction des infos essentielles
    payload = {
        "symbol": data['s'],  # Ex: BTCUSDT
        "price": float(data['p']),  # Prix actuel
        "time": data['E']  # Timestamp de l'événement
    }

    # Envoi vers le topic 'crypto-prices'
    producer.produce(
        'crypto-prices',
        value=json.dumps(payload).encode('utf-8'),
        callback=delivery_report
    )
    # On force l'envoi immédiat
    producer.flush()


def on_error(ws, error):
    print(f"Erreur WebSocket : {error}")


# URL du flux temps réel de Binance (Trade stream pour BTC/USDT)
socket = "wss://stream.binance.com:9443/ws/btcusdt@trade"

ws = websocket.WebSocketApp(
    socket,
    on_message=on_message,
    on_error=on_error
)

print("🚀 Lancement du Producer... Appuie sur Ctrl+C pour arrêter.")
ws.run_forever()