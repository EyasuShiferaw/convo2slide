import os
import re
import logging
import aisuite as ai
from dotenv import load_dotenv


from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_exponential


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

# Load environment variables from .env file
load_dotenv()



@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def get_completion(messages: list[dict], temp=0.75) -> str:
    """ Generate a completion for the given messages and model.
    
    Args:
        messages (list): A list of messages, where each message is a dictionary with the following keys:
            - role: The role of the sender of the message, e.g. "user" or "system".
            - content: The text of the message.
        model (str): The model to use to generate the completion.
    
    Returns:
        str: The generated completion.
    """
    logger.info(f"Getting completion for messages:")
    client = ai.Client()
    client.configure({"openai" : {
  "api_key": os.environ.get("API_KEY"),
}})
    response = None
    model = "openai:gpt-4o"
    try:
        logger.info("Trying to get completion for messages")
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp
            )
    except Exception as e:
        logger.error(f"Error getting completion for messages.\nException: {e}")
        raise  # Allow @retry to handle the exception
    else:
        logger.info(f"successfully got completion for messages")
        return response.choices[0].message.content
    

def parse_research_papers(xml_string: str) -> list[dict]:
    """
    Parse XML string containing research paper analyses into a list of dictionaries.
    
    Args:
        xml_string (str): XML string containing research paper analyses
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing paper analyses
    """
    logger.info("Parsing research papers from XML")
    
    
    clean_xml = '\n'.join(line for line in xml_string.split('\n') 
                         if not line.strip() == 'xml')
    
    # Create root element from string
    try:
        root = ET.fromstring(clean_xml)
    except ET.ParseError:
        # If still having issues, try to extract just the research paper analyses
        start_idx = clean_xml.find('<research_paper_analysis>')
        end_idx = clean_xml.rfind('</research_paper_analysis>') + len('</research_paper_analysis>')
        if start_idx != -1 and end_idx != -1:
            analyses_xml = f"<root>{clean_xml[start_idx:end_idx]}</root>"
            root = ET.fromstring(analyses_xml)
        else:
            logger.error("Failed to find research paper analysis tags in XML")
            raise 
    
    papers = []
    
    for paper in root.findall('.//research_paper_analysis'):
        paper_dict = {}
        for child in paper:
            text = ' '.join(child.text.split()) if child.text else ''
            paper_dict[child.tag] = text
            
        papers.append(paper_dict)

    logger.info("Successfully parsed research papers from XML")
    return papers


def parse_topics(xml_string: str) -> dict:
    """
    Parse XML string containing research topic suggestions into a dictionary of keywords and terms.
    
    Args:
        xml_string (str): XML string containing topic suggestions
        
    Returns:
        dict: A dictionary containing two lists: 'keywords' and 'terms'
    """
    logger.info("Parsing topics from XML using BeautifulSoup")
 
    try:
        # Parse the cleaned XML using BeautifulSoup
        soup = BeautifulSoup(xml_string, 'xml')
        logger.debug(f"BeautifulSoup parsed XML: {soup.prettify()}")
    except Exception as e:
        logger.error(f"Error parsing XML with BeautifulSoup: {e}")
        raise
    
    # Extract keywords from <specific_keywords>
    keywords = [keyword.get_text() for keyword in soup.find_all('keyword')]
    logger.info(f"Extracted keywords: {keywords}")
    
    # Extract terms from <technical_terms>
    terms = [term.get_text() for term in soup.find_all('term')]
    logger.info(f"Extracted terms: {terms}")

    logger.info("Successfully parsed topics from XML")

    return keywords + terms 



def parse_research_data(xml_content: str) -> list[dict]:
    """ Parse the research papers from the given XML content using BeautifulSoup.
    
    Args:
        xml_content(str): content in the xml format
    
    Returns:
        dict: The extracted research paper data.
    """
    logging.info(f"Parsing data from XML")
  
    try: 
        # Parse the XML content with BeautifulSoup
        soup = BeautifulSoup(xml_content, 'xml')
    except Exception as e:
        logger.error(f"Error parsing XML content with BeautifulSoup.\nException: {e}")
        return {}
    research_data = []
    
    for section in soup.find_all('entry'):
            title = section.find('title').text.strip() if section.find('title') else "Unknown"
            summary = section.find('summary').text.strip() if section.find('summary') else "Unknown"
            links = section.find('id').text.strip() if section.find('id') else ""
            research_data.append({"title": title, "summary": summary, "links": links})      
            

    logging.info(f"Successfully parsed research paper from XML")
    return research_data

