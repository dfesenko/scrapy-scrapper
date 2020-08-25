# scrapy-scrapper
Scrapy scrapper for collecting information about 
Morgan Lewis employees (https://www.morganlewis.com/our-people)

## About
Script collects the following data about people:

* Url to the employee profile
* Photo url
* Full name
* Position
* Phone numbers
* Email
* Services
* Sectors
* Publications
* Person brief
* DateTime of scraping the profile

As the result, it generates a CSV file.

## Technologies
* Scrapy 2.1.0
* RabbitMQ 3.8.5 (optional)
* MySQL 8.0.21 (optional)

## How to install and run
1. Clone the repo: `git clone https://github.com/dfesenko/scrapy-scrapper.git`. 
Go inside the `scrapy-scrapper` folder: `cd scrapy-scrapper`.
2. Create a virtual environment: `python -m venv venv`.
3. Activate virtual environment: `source venv/bin/activate`.
4. Install dependencies into the virtual environment: 
`pip install -r requirements.txt`.
5. Change directory: `cd morganlewis`.
6. Issue the following command:
`scrapy crawl morganlewis -o morganlewis_people.csv -t csv`.
7. Now the script should be started. The `morganlewis_people.csv` file should 
appear in the directory. The script populates it with data. 
8. If you want to change some scrapper parameters you can explore the 
`/morganlewis/morganlewis/settings.py` file. For example, you can try to
tweak the `DOWNLOAD_DELAY` there to speed up scrapping.


## *[Optional]* Publishing of scrapped items into MySQL database
Besides saving data into CSV file, it is also possible to populate the MySQL database. 
This functionality is implemented using Scrapy pipelines and RabbitMQ queue. The workflow is as follows:
1. Scrapy pipeline is configured to publish scrapped items to the RabbitMQ queue (see `pipelines.py`).
It can be considered as producer of data.
2. RabbitMQ worker (`db_writer_worker.py`) can be considered as consumer. It takes items from RabbitMQ
queue and inserts them into MySQL database (table `People`).

There is a range of parameters that you can change. In the `settings_local.py` file you can specify
MySQL database host, port, database name, credentials. The default RabbitMQ queue is called 
`test_queue`. It can be changed in the `pipelines.py` and `db_writer_worker.py` files.

To start the scraper use the same command as before:  
`scrapy crawl morganlewis -o morganlewis_people.csv -t csv`.

In the separate Terminal window you should start the worker:  
`python db_writer_worker.py`

You can start as many workers, as you want. The load will be balanced among them.

The RabbitMQ and MySQL must be installed and properly configured beforehand.

The SQL commands for database and table in MySQL creation you can find in the `sql.txt` file.


