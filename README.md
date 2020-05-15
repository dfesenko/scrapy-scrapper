# scrapy-scrapper
Scrapy scrapper for collection information about 
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


