import logging
from scrape import scrape_chat_messages
from prompt import user_prompt, system_prompt
from concurrent.futures import ThreadPoolExecutor
from utility import get_completion, parse_topics



# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



TEMP = """
User:  does seleumin work on aws instance?
Assistant:  Yes, Selenium can work on an AWS instance. However, there are some specific configurations and considerations depending on your use case:

Steps to Set Up Selenium on an AWS Instance

Launch an AWS Instance: Choose an appropriate instance type and operating system (Ubuntu, Amazon Linux, etc.).

Install Required Dependencies:

Update the system:
bash
Copy
sudo apt update && sudo apt upgrade -y

Install Python and pip (if using Python):
bash
Copy
sudo apt install python3 python3-pip -y

Install other dependencies for Selenium and browser drivers:
bash
Copy
sudo apt install wget unzip xvfb -y


Install Selenium: Use pip to install Selenium:

bash
Copy
pip install selenium


Set Up a Web Driver: Selenium requires a compatible web driver (e.g., ChromeDriver for Google Chrome or GeckoDriver for Firefox):

Install Google Chrome and ChromeDriver:
bash
Copy
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt install -f  # Resolve dependencies

CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
wget https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/

Alternatively, install GeckoDriver for Firefox.

Headless Mode (Optional): Since AWS instances often lack a display, you may need to use Selenium in headless mode:

python
Copy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://example.com")
print(driver.title)
driver.quit()


Run in a Virtual Display (Optional): If headless mode is not sufficient for your use case, you can use Xvfb (a virtual framebuffer) to simulate a display:

bash
Copy
sudo apt install xvfb
xvfb-run -a python3 your_script.py

Common Considerations
Security Groups: Ensure the instance's security groups allow traffic to and from the required endpoints.
IAM Role: Attach an appropriate IAM role to the instance if your Selenium script needs to access other AWS services.
Resource Usage: Be mindful of the instance type and resources (CPU and memory) when running resource-intensive Selenium scripts.
Testing

After setup, run a test script to verify that Selenium works as expected.
User:  can i request wait for the page to load before fetc the data?
Assistant:  Yes, in Selenium, you can wait for the page to load before interacting with elements or fetching data. Selenium provides several ways to implement waits, which are crucial for ensuring the page or specific elements are fully loaded before performing actions.

Types of Waits in Selenium
1. Implicit Wait

Implicit wait makes the WebDriver poll the DOM for a specified time when trying to find an element. It's a global setting and applies to all element searches.

python
Copy
from selenium import webdriver

driver = webdriver.Chrome()
driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to appear
driver.get("https://example.com")
element = driver.find_element("id", "example-id")  # Selenium will wait if the element is not immediately available
driver.quit()

2. Explicit Wait

Explicit wait waits for specific conditions to be met before proceeding. It's more flexible than implicit wait.

python
Copy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://example.com")

# Wait for an element to become clickable
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "example-id"))
)
print("Element is ready!")
driver.quit()


Common Expected Conditions:

presence_of_element_located: Waits for an element to be present in the DOM.
element_to_be_clickable: Waits for an element to be clickable.
visibility_of_element_located: Waits for an element to be visible.
text_to_be_present_in_element: Waits for specific text to appear in an element.
3. Fluent Wait

Fluent wait is similar to explicit wait but allows you to define the polling frequency and handle exceptions during the wait.

python
Copy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://example.com")

wait = WebDriverWait(driver, 10, poll_frequency=1, ignored_exceptions=[Exception])
element = wait.until(EC.presence_of_element_located((By.ID, "example-id")))

print("Element found!")
driver.quit()

Example: Wait
User:  yeah but i don't have access to it 
Assistant:  If you don't have access to the webpage or cannot modify its code directly, you can still wait for the page to load or specific elements to appear by using Selenium's JavaScript execution or checking the page's loading state indirectly. Here are alternative approaches:

1. Wait for Page Load via JavaScript (document.readyState)

Selenium allows you to execute JavaScript code to check the page's loading status. You can wait until the page is fully loaded:

python
Copy
from selenium import webdriver

driver = webdriver.Chrome()

driver.get("https://example.com")

# Wait for the page to be fully loaded
while True:
    if driver.execute_script("return document.readyState") == "complete":
        break

print("Page fully loaded!")
driver.quit()


This method ensures the entire page is loaded by waiting until document.readyState equals "complete".

2. Wait for Specific Elements

If you can't rely on the page's load status but need to wait for specific elements (like tables, images, or dynamic content), use explicit waits with Selenium's ExpectedConditions.

Example:

python
Copy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

driver.get("https://example.com")

# Wait for a specific element to load
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "example-id"))
    )
    print("Element loaded!")
except Exception as e:
    print("Element not found within the time limit:", e)

driver.quit()

3. Wait for Network Requests to Complete

You can monitor network activity by injecting JavaScript that listens for ongoing XMLHttpRequests or fetch calls.

python
Copy
from selenium import webdriver
import time

driver = webdriver.Chrome()

driver.get("https://example.com")

# Wait for network activity to finish
while True:
    active_requests = driver.execute_script(
        "return window.performance.getEntriesByType('resource').filter(r => r.initiatorType === 'fetch' || r.initiatorType === 'xmlhttprequest').length;"
    )
    if active_requests == 0:
        break
    time.sleep(1)

print("All network requests completed!")
driver.quit()

4. Use Sleep as a Last Resort

If none of the above methods are feasible due to restrictions, you can introduce a delay using time.sleep(). This is less efficient and less reliable but may work as a quick fix.

python
Copy
import time
from selenium import webdriver

driver = webdriver.Chrome()

driver.get("https://example.com")

# Fixed wait time
time.sleep(10)  # Wait 10 seconds
print("Assuming page is loaded!")
driver.quit

Assistant:  Yes, there are several alternatives to Selenium for fetching data and interacting with web pages, depending on your requirements (e.g., dynamic content loading, scraping static or interactive sites). Here's an overview of some alternatives:

1. Playwright

Playwright is a modern alternative to Selenium. It's faster, more reliable, and supports multiple browsers out of the box. Playwright can handle dynamic content and waiting for elements efficiently.

Key Features:
Supports headless and full-browser automation.
Provides built-in waiting mechanisms for elements and page load.
Supports multiple languages (Python, JavaScript, C#, and Java).
Example in Python:
python
Copy
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")

    # Wait for a specific element
    page.wait_for_selector("#example-id")

    print(page.title())
    browser.close()

2. Puppeteer

Puppeteer is a Node.js library that provides high-level APIs to control Chrome or Chromium. It’s great for dynamic content and rendering JavaScript-heavy pages.

Key Features:
Excellent for JavaScript-heavy sites.
Easy to integrate with Node.js.
Can generate PDFs, take screenshots, and scrape data.
Example:
javascript
Copy
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://example.com');
  
  // Wait for an element
  await page.waitForSelector('#example-id');
  
  const title = await page.title();
  console.log(title);
  await browser.close();
})();

3. BeautifulSoup (with Requests)

If the site doesn’t rely heavily on JavaScript (static content), you can use BeautifulSoup with Requests for simple scraping.

Key Features:
Lightweight and easy to use.
Best for static sites without dynamic JavaScript.
Doesn't require a browser.
Example:
python
Copy
import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extract specific content
title = soup.find("title").text
print(title)

4. HTTPX with Async

For fetching and interacting with APIs or sites with lightweight dynamic content, HTTPX is a powerful alternative.

Key Features:
Asynchronous HTTP requests for better performance.
Works well with API-based or lightweight sites.
Example:
python
Copy
import httpx
from bs4 import BeautifulSoup

async def fetch():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com")
        soup = BeautifulSoup(response.text, "html.parser")
        print(soup.title.string)

import asyncio
asyncio.run(fetch())

5. Scrapy

Scrapy is a framework designed for web scraping. It’s highly efficient and scalable for crawling and scraping large datasets.

Key Features:
Asynchronous scraping.
Built-in support for item pipelines, middleware, and more.
Best for large-scale scraping projects.
Example:
python
Copy
import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"
    start_urls = ['https://example.com']

    def parse(self, response):
        title = response.css('title::text').get()
        print(title)

6. API (Preferred When Available)

If the website provides an API, use it instead of scraping. APIs are faster, more reliable, and often provide the same data.

Example:
python
Copy
import requests

url = "https://api.example.com/data"
response = requests.get(url, headers={"Authorization": "Bearer YOUR_TOKEN"})
data = response.json()
print(data)

7. Headless Browsers (Direct Interaction)
PhantomJS (now deprecated but still usable for some cases).
Headless Chrome (can be controlled via DevTools Protocol).
Choosing the Right Tool
JavaScript-heavy sites: Playwright or Puppeteer.
Static sites: BeautifulSoup or Requests.
Large-scale scraping: Scrapy.
API availability: Direct API requests.
Need for browser emulation: Playwright, Puppeteer, or Selenium.

Let me know if you need further guidance on setting up any of these tools!
User:  does it works in aws instance
Assistant:  Yes, all the mentioned alternatives to Selenium can work on an AWS instance, including Playwright, Puppeteer, BeautifulSoup, Scrapy, and others. However, the setup process may vary depending on the tool and the instance type. Here's how to set them up for use on an AWS instance:

1. Playwright on AWS

Playwright works well on AWS, but you need to install its dependencies.

Steps:

Install Playwright and Dependencies:

bash
Copy
sudo apt update
sudo apt install -y libnss3 libatk1.0-0 libx11-xcb1 libxcomposite1 libxrandr2 libasound2 libpangocairo-1.0-0
pip install playwright
playwright install


Run Playwright Script: Use --headless mode to avoid display issues:

python
Copy
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()

Notes:
Ensure your instance has sufficient CPU/memory resources if running multiple Playwright browsers.
Use Xvfb if graphical rendering is needed without --headless.
2. Puppeteer on AWS

Puppeteer works seamlessly on AWS with Node.js installed.

Steps:

Install Node.js:

bash
Copy
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs


Install Puppeteer:

bash
Copy
npm install puppeteer


Run Puppeteer Script: Use headless mode for better compatibility:

javascript
Copy
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto('https://example.com');
    console.log(await page.title());
    await browser.close();
})();

Notes:
Similar to Playwright, use Xvfb if you need non-headless mode.
3. BeautifulSoup (with Requests) on AWS

Since BeautifulSoup doesn't rely on a browser, it's lightweight and easy to set up on AWS.

Steps:

Install Dependencies:

bash
Copy
sudo apt update
sudo apt install -y python3 python3-pip
pip install beautifulsoup4 requests


Run BeautifulSoup Script:

python
Copy
import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
print(soup.title.string)

Notes:
No graphical interface or special setup is needed.
4. Scrapy on AWS

Scrapy is ideal for large-scale scraping projects and works on AWS.

Steps:

Install Scrapy:

bash
Copy
pip install scrapy


Run Scrapy Project: Example spider:

bash
Copy
scrapy startproject myproject
cd myproject
scrapy genspider example example.com
scrapy crawl example

5. Headless Browsers (Xvfb for Non-Headless Mode)

For Playwright, Puppeteer, or Selenium in non-headless mode, you need a virtual display like Xvfb.

Steps:

Install Xvfb:

bash
Copy
sudo apt install -y xvfb


Run Script with Xvfb: Use xvfb-run to wrap your command:

bash
Copy
xvfb-run -a python3 your_script.py

Recommendations
For JavaScript-heavy sites: Use Playwright or Puppeteer.
For lightweight scraping: Use BeautifulSoup or Scrapy.
Use headless mode whenever possible for better performance and ease of use on AWS.

Let me know if you need more specific setup details or troubleshooting tips!
"""


class Convo2Slide():

    def __init__(self, url) -> None:
        self.url = url 
        self.chat = []

    
    def construct_messages(self, user_prompt: str, system_prompt: str) -> list[dict]:
        """
        Construct the system and user prompts for the OpenAI API.
        
        Returns:
            list: A list of dictionaries representing the system and user prompts.
        """
        logger.info("Constructing messages for the API.")
        try:
            chat_data = [f"{message['role'].capitalize()}:  {message['content']}" for message in self.chat]
        except:
            logging.error("Failed to parse chat data - invalid dictionary format)")
            return []
        else:
            # temp = "\n".join(chat_data)
            temp = TEMP
            print(temp)
            return [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt.format(chat_data=temp)}   
                ]    
              
    def pipeline(self):
        """
        Execute the research assistance pipeline to gather and process research data.

        """

        logger.info("Executing convo2slide research) assistance pipeline.")
        
        # self.chat = scrape_chat_messages(self.url)

        # if self.chat == []:
        #     raise Exception("Empty list of chat messages")
        #     return None
            
        messages = self.construct_messages(user_prompt, system_prompt)

        if len(messages) == 0:
            raise Exception("Empty list of messages")
            return None

        response = get_completion(messages)
        print(response)
        title, subtitle, slides_data = parse_topics(response)
        return title, subtitle, slides_data
    

        
    

# if __name__ == "__main__":
#     url = "https://chatgpt.com/share/67890791-a098-8007-be1f-a16143aa0ecb"
#     convo2slide = Convo2Slide(url)
#     convo2slide.pipeline()


   

