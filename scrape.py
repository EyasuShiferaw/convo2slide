from playwright.sync_api import sync_playwright
from time import sleep
from types import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def scrape_chat_messages(url:str) -> List[Dict[str, str]]:

    logging.info(f"Start scraping chat messages")
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url)
            sleep(15)

        except:
            logging.error(f"Can't scrape chat messages from the given url:{url}")
            return []
        
        else:
            messages = page.query_selector_all('div[data-message-author-role]')
            chat_data = [] 
            for message in messages:
                role = message.get_attribute('data-message-author-role')  # user or assistant
                content = message.inner_text()  # Extract message text
                chat_data.append({'role': role, 'content': content})
            
            browser.close()
            
            return chat_data
    


url="https://chatgpt.com/share/67890791-a098-8007-be1f-a16143aa0ecb"
chat_messages = scrape_chat_messages(url)

# Print messages in correct order
for message in chat_messages:
    print(f"{message['role'].capitalize()}: {message['content']}")


