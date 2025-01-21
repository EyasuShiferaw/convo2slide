import os
import sys
import logging
import subprocess
from time import sleep
from pathlib import Path
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright
from tenacity import retry, stop_after_attempt, wait_exponential


# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def install_browser_forcefully():
    """
    Force a clean installation of Playwright browser with all dependencies.
    Raises subprocess.CalledProcessError if installation fails.
    """
    logger.info("Starting forced browser installation")
    try:
        # Install browser and dependencies
        subprocess.run([sys.executable, "-m", "playwright", "install","--with-deps", "chromium"],
                      check=True, capture_output=True)
        
        logger.info("Browser installation completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Browser installation failed: {e.stdout.decode() if e.stdout else ''}")
        raise



def scrape_chat_messages(url:str) -> List[Dict[str, str]]:
    """
    Scrape chat messages from a given URL using Playwright.
    
    Args:
        url (str): The URL to scrape chat messages from
        
    Returns:
        List[Dict[str, str]]: A list of dictionaries containing chat messages with 'role' and 'content' keys.
                             Returns empty list if scraping fails.
    """
    logger.info(f"Attempting to scrape chat messages from {url}")
   
      
    try:
        install_browser_forcefully()
        print(f"Playwright and browser installation check completed successfully:")
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

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

            logger.info("Successfully scraped chat messages")
            
            return chat_data
    
