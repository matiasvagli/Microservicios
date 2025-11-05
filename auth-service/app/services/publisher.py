# servicio para publicar eventos en RabbitMQ
import json
import os
import pika

def publish_user_registered(user_id: str):
    try:
        print(f"Intentando publicar evento para usuario {user_id}")
        
        # Leer configuración desde variables de entorno
        host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        port = int(os.getenv("RABBITMQ_PORT", "5672"))
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASS", "guest")
        queue = os.getenv("RABBITMQ_QUEUE", "user_registered")
        
        print(f"Configuración RabbitMQ: host={host}, port={port}, queue={queue}")

        # Preparar conexión y mensaje
        body = json.dumps({"user_id": user_id})
        credentials = pika.PlainCredentials(user, password)
        print(f"Intentando establecer conexión con RabbitMQ...")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
        print(f"Conexión establecida con RabbitMQ")
        
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        print(f"Cola '{queue}' declarada")
        
        channel.basic_publish(exchange="", routing_key=queue, body=body)
        print(f"Mensaje enviado a RabbitMQ: {body}")

        connection.close()
        print(f"Conexión cerrada correctamente")
    except Exception as e:
        print(f"Error publicando mensaje en RabbitMQ: {str(e)}")
        print(f"Detalles del error: {type(e).__name__}")
