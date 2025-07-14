import pika

RABBITMQ_URL = "amqp://username:password@localhost:5672/"

def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    return connection

def publish_message(queue_name, message):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()

def consume_messages(queue_name, callback):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    def on_message(ch, method, properties, body):
        callback(body.decode())
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    channel.start_consuming()