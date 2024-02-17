# Scrapy settings for tutorial project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BOT_NAME = "hgpt"
ROOT_URL = os.getenv("ROOT_URL")
OUT_PATH = os.getenv("OUT_PATH", "data/real_estates.jsonl")
MAX_DETAIL_PAGES = int(os.getenv("MAX_DETAIL_PAGES", "1"))

SPIDER_MODULES = ["hgpt.spiders"]
NEWSPIDER_MODULE = "hgpt.spiders"

LOG_LEVEL = "INFO"
LOG_FILE = f"{BOT_NAME}.log"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "hgpt"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 20 * 1000,  # 5 seconds
}

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {"hgpt.pipelines.DistancePipeline": 300}

FEEDS = {
    OUT_PATH: {
        "format": "jsonlines",
        "encoding": "utf8",
        "store_empty": False,
        "indent": None,
        "item_export_kwargs": {
            "export_empty_fields": True,
        },
    },
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
