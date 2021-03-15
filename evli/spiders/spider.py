import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import EvliItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class EvliSpider(scrapy.Spider):
	name = 'evli'
	start_urls = ['https://www.evli.com/en/news',
				  'https://www.evli.com/blog/funds/page/1'
				  ]

	def parse(self, response):
		post_links = response.xpath('//div[@class="simple-listing__item"]/a/@href | //div[@class="mediakirjasto-feed-item"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next-posts-link"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//p[@class="post-date"]/text()').get()
		title = response.xpath('//h1//text()').get()
		content = response.xpath('//div[@class="post-content-wrapper content-wrapper-small"]//text()[not (ancestor::div[@class="post-content-sidebar"]) and not (ancestor::span[@style="display:none;"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=EvliItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
