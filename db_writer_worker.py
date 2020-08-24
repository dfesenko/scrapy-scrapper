import pika
import json
import sqlalchemy as db

from .settings_local import MYSQL_HOST, MYSQL_PORT, MYSQL_LOGIN, MYSQL_PASSWORD, MYSQL_DATABASE_NAME

engine = db.create_engine(f'mysql+mysqlconnector://'
                          f'{MYSQL_LOGIN}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE_NAME}')

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='test_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def permissive_json_loads(text):
    while True:
        try:
            data = json.loads(text)
        except json.decoder.JSONDecodeError as exc:
            if exc.msg == 'Invalid \\escape':
                text = text[:exc.pos] + '\\' + text[exc.pos:]
            elif exc.msg == "Expecting ',' delimiter":
                text = text[:exc.pos - 1] + '\\' + text[exc.pos:]
            else:
                raise
        else:
            return data


def callback(ch, method, properties, body):
    print(" [x] Received item. Starting publishing to database.")

    json_str = body.decode().replace("'", '"')

    publications_start = json_str.index(', "publications"')
    without_publications = json_str[:publications_start] + "}"

    data_without_publications = permissive_json_loads(without_publications)

    # we should add publications directly as a slice from the json_str
    # due to multiple parsing errors that occur during parsing the `publications` field
    data = dict({"publications": json_str[publications_start + len(', "publications":'): -1]},
                **data_without_publications)

    for key, value in data.items():
        if key == 'phone_numbers':
            data[key] = str(value).replace("'", '')
        elif key in ['services', 'sectors']:
            data[key] = str([element.strip() for element in data[key] if len(element.strip()) > 1]).replace("'", '"')

    sql = f"INSERT INTO People (Url, PhotoUrl, Fullname, Position, Phone_numbers, Email, Services, Sectors, Brief, " \
          f"Publications, ScrappingDate) VALUES ('{data['url']}', '{data['photo_url']}', '{data['full_name']}', " \
          f"'{data['position']}', '{data['phone_numbers']}', '{data['email']}', '{data['services']}', '{data['sectors']}', " \
          f"'{data['person_brief']}', '{data['publications']}', '{data['scrapping_datetime']}');"

    engine.execute(sql)

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='test_queue', on_message_callback=callback)

channel.start_consuming()
