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



def check_playwright_installation(browser: str = "chromium") -> bool:
    """
    Check if Playwright and specified browser are installed.
    
    Args:
        browser (str): Browser to check for. Defaults to "chromium".
                      Options: "chromium", "firefox", "webkit"
    
    Returns:
        bool: True if both Playwright and browser are installed, False otherwise
    """
    # Check if playwright is installed
    try:
        import playwright
    except ImportError:
        print("Playwright not found. Installing playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        
    # Path where Playwright browsers are typically installed
    if sys.platform == "win32":
        browser_path = Path(os.path.expanduser("~")) / "AppData" / "Local" / "ms-playwright"
    elif sys.platform == "darwin":
        browser_path = Path(os.path.expanduser("~")) / "Library" / "Caches" / "ms-playwright"
    else:  # Linux
        browser_path = Path(os.path.expanduser("~")) / ".cache" / "ms-playwright"

    # Check if browser is installed by looking for its directory
    browser_exists = any(
        d.name.startswith(browser) 
        for d in browser_path.glob("*") 
        if d.is_dir()
    ) if browser_path.exists() else False

    if not browser_exists:
        print(f"{browser} browser not found. Installing browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", browser], check=True)
        return True
        
    return True



@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
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
        is_installed = check_playwright_installation("chromium")
        print(f"Playwright and browser installation check completed successfully: {is_installed}")
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
    
