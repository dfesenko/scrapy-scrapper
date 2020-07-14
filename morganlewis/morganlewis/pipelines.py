# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pika


class MorganlewisPipeline:

    def __init__(self, rabbitmq_host, rabbitmq_queue_name):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_queue_name = rabbitmq_queue_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            rabbitmq_host=crawler.settings.get('RABBITMQ_HOST'),
            rabbitmq_queue_name=crawler.settings.get('RABBITMQ_QUEUE_NAME', 'morganlewis_people')
        )

    def open_spider(self, spider):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.rabbitmq_queue_name, durable=True)

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.rabbitmq_queue_name,
            body=str(item),
            properties=pika.BasicProperties(
                delivery_mode=2,
            ))
        return item
