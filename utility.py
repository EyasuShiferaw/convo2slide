import os
import re
import json
import logging
import aisuite as ai
from dotenv import load_dotenv
from typing import Tuple, List, Dict, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

# Load environment variables from .env file
load_dotenv()




@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def get_completion(messages: list[dict], model="openai:gpt-4o") -> str:
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
    model = model
    try:
        logger.info("Trying to get completion for messages")
        response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
    except Exception as e:
        logger.error(f"Error getting completion for messages.\nException: {e}")
        raise  # Allow @retry to handle the exception
    else:
        logger.info(f"successfully got completion for messages")
        return response.choices[0].message.content
    

def parse_topics(xml_string: str) -> Tuple[str, str, List[Dict[str, List[str]]]]:
    """
    Parse an XML string containing slides into structured data.

    Args:
        xml_string (str): XML string containing topic suggestions.

    Returns:
        Tuple[str, str, List[Dict[str, List[str]]]]: A tuple containing:
            - Title of the slides (str).
            - Subtitle of the slides (str).
            - A list of dictionaries with slide titles and bullet points.

    Raises:
        ValueError: If XML parsing fails or required elements are missing.
    """
    logger.info("Parsing topics from XML.")
    print(xml_string)

    try:
        # Parse the XML string using BeautifulSoup
        match = re.search(r"<PowerPoint.*?>.*?</PowerPoint>", xml_string, re.DOTALL | re.IGNORECASE)
        xml_clean = match.group(0)
        soup = BeautifulSoup(xml_clean, 'xml')
        logger.debug("XML successfully parsed with BeautifulSoup.")
    except Exception as e:
        logger.error(f"Failed to parse XML: {e}")
        raise ValueError("Invalid XML input.") from e

    try:
        # Extract title and subtitle
        title = soup.find(re.compile('Title', re.IGNORECASE)).get_text(strip=True)
        subtitle = soup.find(re.compile('Subtitle', re.IGNORECASE)).get_text(strip=True)
        logger.debug(f"Extracted Title: {title}, Subtitle: {subtitle}")
    except AttributeError as e:
        logger.error("Missing required elements in the XML: Title or Subtitle.")
        raise ValueError("XML is missing required elements: Title or Subtitle.") from e

    # Extract slides data
    slides_data = []
    for slide in soup.find_all(re.compile('Slide', re.IGNORECASE)):
        slide_title = slide.find(re.compile('Title', re.IGNORECASE))
        bullet_points = slide.find_all(re.compile('BulletPoint', re.IGNORECASE))

        if slide_title:
            slide_dict = {
                "title": slide_title.get_text(strip=True),
                "points": [point.get_text(strip=True) for point in bullet_points]
            }
            slides_data.append(slide_dict)
            logger.debug(f"Parsed slide: {slide_dict}")

    logger.info("Successfully parsed topics from XML.")

    return title, subtitle, slides_data


def extract_json(text: str) -> Optional[dict]:

    logger.info("start extracting JSON from text.")

    # Use regex to extract the JSON part
    json_match = re.search(r'\{.*\}', text, re.DOTALL)

    if json_match:
        json_str = json_match.group(0)  # Extract matched JSON string
        data_dict = json.loads(json_str)  # Convert JSON string to dictionary
        logger.info("Successfully extracted JSON from text.")
        temp = data_dict["presentation"]
        return temp["title"], temp["subtitle"], temp["slides"]
    else:
        logger.error("No JSON found.")
        return None


def create_selenium_presentation(title: str, subtitle: str, slides_data: list):
    """
    Create a PowerPoint presentation using python-pptx with consistent styling.
    
    Args:
        title (str): The title of the presentation
        subtitle (str): The subtitle of the presentation 
        slides_data (list): List of dictionaries containing slide titles and bullet points
        
    Returns:
        Presentation: A python-pptx Presentation object with formatted slides
    """
    logger.info("Creating PowerPoint presentation with selenium.")
    # Create presentation
    prs = Presentation()
    
    # Define consistent colors
    TITLE_COLOR = RGBColor(44, 62, 80)  # Dark blue-gray
    BULLET_COLOR = RGBColor(52, 73, 94)  # Lighter blue-gray
    
    # Create title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    
    # Set main title
    title_shape = slide.shapes.title
    title_shape.text = title
    title_shape.text_frame.paragraphs[0].font.size = Pt(44)
    title_shape.text_frame.paragraphs[0].font.color.rgb = TITLE_COLOR
    
    # Set subtitle
    subtitle_shape = slide.placeholders[1]
    subtitle_shape.text =subtitle
    subtitle_shape.text_frame.paragraphs[0].font.size = Pt(32)
    subtitle_shape.text_frame.paragraphs[0].font.color.rgb = BULLET_COLOR
    
    # Create content slides
    for slide_data in slides_data:
        # Use content slide layout
        content_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(content_slide_layout)
        
        # Add title
        title_shape = slide.shapes.title
        title_shape.text = slide_data["title"]
        title_shape.text_frame.paragraphs[0].font.size = Pt(40)
        title_shape.text_frame.paragraphs[0].font.color.rgb = TITLE_COLOR
        
        # Add bullet points
        body_shape = slide.shapes.placeholders[1]
        tf = body_shape.text_frame
        
        # Clear default text
        if tf.text:
            tf.clear()
        
        # Add bullet points with formatting
        for idx, point in enumerate(slide_data["points"]):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = point
            p.font.size = Pt(24)
            p.font.color.rgb = BULLET_COLOR
            p.level = 0
            
            # Add spacing between bullet points
            p.space_after = Pt(12)
      
    logger.info("Successfully created PowerPoint presentation with selenium.")
    return prs
