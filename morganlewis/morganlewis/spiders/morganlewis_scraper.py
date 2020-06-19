import scrapy
import json

from datetime import datetime


class MorganlewisSpider(scrapy.Spider):
    name = 'morganlewis'

    def generate_paging_url(self, page_num, num_per_page=100):
        return f"https://www.morganlewis.com/api/custom/peoplesearch/search?keyword=&category" \
               f"=bb82d24a9d7a45bd938533994c4e775a&sortBy=lastname&pageNum={page_num}&numberPerPage={num_per_page}" \
               f"&numberPerSection=5&enforceLanguage=&languageToEnforce=&school=&position=&location=&court=&judge" \
               f"=&isFacetRefresh=false "

    def start_requests(self):
        yield scrapy.Request(url=self.generate_paging_url(page_num=1), callback=self.parse)

    def parse(self, response):
        # follow links to profiles pages
        for href in response.css('div.c-content_team__card-info>a:first-child ::attr(href)').getall():
            yield response.follow(href, callback=self.parse_profile)

        # follow next page
        last_page_num = response.css('div.c-pagination a.last ::attr(data-pagenum)').get()
        current_page_num = int(response.css('div.c-pagination a.selected ::attr(data-pagenum)').get())
        if last_page_num and current_page_num < int(last_page_num):
            yield response.follow(self.generate_paging_url(page_num=current_page_num + 1), callback=self.parse)

    def parse_profile(self, response):

        def get_absolute_photo_url(response):
            relative_photo_url = response.css('div.thumbnail img ::attr(src)').get()
            return response.urljoin(relative_photo_url)

        def get_services(response):
            # detect in which section Services are - in case Services and Regions sections will be swapped
            first_block_person_depart_info_head = response.css(
                'section.person-depart-info:first-of-type h2 ::text').get()
            if first_block_person_depart_info_head == 'Services':
                return response.css('section.person-depart-info:first-of-type a ::text').getall()
            else:
                return response.css('section.person-depart-info:nth-of-type(2) a ::text').getall()

        def get_person_id(response):
            vcard_url = response.css('div.thumbnail-details p.v-card a::attr(href)').get()
            return vcard_url.split('itemId=%7B')[-1][:-3]

        def get_publications(response):
            profile_data = response.meta['scrapped_data']
            profile_data['publications'] = response.css('a::attr(title)').getall()
            yield profile_data

        profile_data = {
            'url': response.request.url,
            'photo_url': get_absolute_photo_url(response),
            'full_name': response.css('section.person-heading span[itemprop=name] ::text').get(),
            'position': response.css('section.person-heading h2 ::text').get(),
            'phone_numbers': response.css('div.thumbnail-details p[itemprop=telephone] a ::text').getall(),
            'email': response.css('div.thumbnail-details a[itemprop=email] ::text').get(),
            'services': get_services(response),
            'sectors': response.css('div.person-depart-info a ::text').getall(),
            'person_brief': response.css('div.people-intro p ::text').get(),
            'scrapping_datetime': datetime.now().strftime("%Y:%m:%d, %H:%M:%S")
        }

        yield scrapy.Request(url="https://www.morganlewis.com/api/sitecore/accordion/getaccordionlist",
                             callback=get_publications,
                             method='POST',
                             meta={'scrapped_data': profile_data},
                             body=json.dumps({'itemId': '{' + get_person_id(response) + '}',
                                              'itemType': 'publicationitemlist',
                                              'printView': ''}),
                             headers={'Content-Type': 'application/json'})


