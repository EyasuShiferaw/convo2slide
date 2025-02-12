import os
import re
import json
import logging
import aisuite as ai
from dotenv import load_dotenv
from typing import Tuple, List, Dict, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE, PP_PARAGRAPH_ALIGNMENT
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

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
                temperature=1.0,
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
    """
    Extract JSON data from text string.

    Args:
        text (str): Text containing JSON data.

    Returns:
        Optional[tuple]: A tuple containing:
            - Title of the slides (str)
            - Subtitle of the slides (str) 
            - A list of dictionaries with slide data
        Returns None if no valid JSON is found.

    """
    logger.info("start extracting JSON from text.")

    # Use regex to extract the JSON part
    json_match = re.search(r'\{.*\}', text, re.DOTALL)

    if json_match:
        json_str = json_match.group(0)  # Extract matched JSON string
        data_dict = json.loads(json_str)  # Convert JSON string to dictionary
        logger.info("Successfully extracted JSON from text.")
        return data_dict
    else:
        logger.error("No JSON found.")
        return None


def apply_theme_color(shape, rgb):
    """Apply RGB color to shape fill
    Args:
        shape: The PowerPoint shape object to apply color to
        rgb: Tuple of RGB color values (red, green, blue)
    """
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(*rgb)

def add_bullet_point(tf, text, theme_colors):
    """Helper function to add properly formatted bullet points
    Args:
        tf: Text frame to add bullet point to
        text: Text content of the bullet point
        theme_colors: Dictionary containing theme color definitions
    
    Returns:
        The created paragraph object
    """
    p = tf.add_paragraph()
    p.text = f"• {text}"
    p.font.size = Pt(20)
    
    if any(char in text for char in ["=", "+", "^", "*", "/"]):
        p.font.color.rgb = theme_colors['accent']
    else:
        p.font.color.rgb = theme_colors['text']

    p.space_after = Pt(12)
    p.level = 0
    return p

def estimate_text_height(text, font_size, width_inches):
    """Estimate the height needed for text based on font size and width"""
    chars_per_line = int((width_inches * 96) / (font_size * 0.5))
    lines = len(text) / chars_per_line
    return (lines * font_size * 1.5) / 72

def create_content_slide(prs, slide_data, idx, THEME_COLORS, content=None, is_continuation=False):
    """Create a single content slide with pagination support"""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    
    # Background
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0,
        prs.slide_width, prs.slide_height
    )
    background.fill.solid()
    background.fill.fore_color.rgb = RGBColor(248, 248, 248)
    
    # Left bar
    left_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        0, 0, Inches(0.25), prs.slide_height
    )
    apply_theme_color(left_bar, (0, 75, 135))
    
    # Title
    title_text = slide_data.get('title', f'Slide {idx}')
    if is_continuation:
        title_text += " (Continued)"
    
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.5),
        Inches(12), Inches(1)
    )
    title_frame = title_box.text_frame
    title_para = title_frame.add_paragraph()
    title_para.text = title_text
    title_para.font.size = Pt(44)
    title_para.font.bold = True
    title_para.font.color.rgb = THEME_COLORS['primary']
    
    # Accent bar
    accent_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.5), Inches(1.4),
        Inches(2), Inches(0.06)
    )
    apply_theme_color(accent_bar, (255, 127, 0))
    
    SPACE_AFTER_PARAGRAPH = Inches(0.1)  # Space after paragraph
    SPACE_BETWEEN_BULLETS = Inches(0.1)  # Space between bullet points
    SPACE_BEFORE_BULLETS = Inches(0.1)   # Space before bullet point section
    
    # Font size constants
    CONTENT_FONT_SIZE = Pt(20)  # Consistent font size for all content
    
    current_y = Inches(1.8)
    max_y = Inches(6.5)
    
    if content:
        # Add paragraph if it exists
        if content.get('paragraph'):
            content_box = slide.shapes.add_textbox(
                Inches(0.5), current_y,
                Inches(12), Inches(4)
            )
            tf = content_box.text_frame
            tf.word_wrap = True
            
            p = tf.add_paragraph()
            p.text = content['paragraph']
            p.font.size = Pt(20)
            p.font.color.rgb = THEME_COLORS['text']
            p.space_after = Pt(24)
            
            current_y += Inches(estimate_text_height(content['paragraph'], 20, 12) + 0.1)
        
        # Add bullet points if they exist
        if content.get('bullet_points'):
            if content.get('paragraph'):  # Add extra space if we had a paragraph
                current_y += Inches(0.3)
            
            bullet_box = slide.shapes.add_textbox(
                Inches(0.5), current_y,
                Inches(12), Inches(4.5)
            )
            tf = bullet_box.text_frame
            tf.word_wrap = True
            
            for point in content['bullet_points']:
                bullet_para = add_bullet_point(tf, point, THEME_COLORS)
                current_y += Inches(estimate_text_height(point, 20, 11) + 0.1)
   
    else:
        # Add paragraph if it exists
        paragraph_text = slide_data.get('paragraph')
        if paragraph_text:
            content_box = slide.shapes.add_textbox(
                Inches(0.5), current_y,
                Inches(12), Inches(4)
            )
            tf = content_box.text_frame
            tf.word_wrap = True
            
            p = tf.add_paragraph()
            p.text = paragraph_text
            p.font.size = CONTENT_FONT_SIZE  # Updated font size
            p.font.color.rgb = THEME_COLORS['text']
            p.space_after = Pt(24)
            
            # Adjust estimation for new font size
            current_y += Inches(estimate_text_height(paragraph_text, 20, 12)) + SPACE_AFTER_PARAGRAPH
        
        # Add bullet points if they exist
        bullet_points = slide_data.get('bullet_points', [])
        if bullet_points and current_y <= max_y:
            current_y += SPACE_BEFORE_BULLETS
            
            bullet_box = slide.shapes.add_textbox(
                Inches(0.5), current_y,
                Inches(12), Inches(4.5)
            )
            tf = bullet_box.text_frame
            tf.word_wrap = True
            
            for point in bullet_points:
                if current_y > max_y:
                    return False, bullet_points[bullet_points.index(point):]
                bullet_para = add_bullet_point(tf, point, THEME_COLORS)
                current_y += Inches(estimate_text_height(point, 20, 11)) + SPACE_BETWEEN_BULLETS
    
    # Slide number
    slide_number = slide.shapes.add_textbox(
        Inches(12), Inches(6.8),
        Inches(0.5), Inches(0.3)
    )
    slide_number_frame = slide_number.text_frame
    slide_number_para = slide_number_frame.add_paragraph()
    slide_number_para.text = str(idx)
    slide_number_para.font.size = Pt(14)
    slide_number_para.font.color.rgb = THEME_COLORS['primary']
    slide_number_para.alignment = PP_ALIGN.RIGHT
    
    return True, []

def estimate_total_height(paragraph_text, bullet_points, font_size=20):
    """Estimate total height needed for both paragraph and bullet points"""
    total_height = 0
    
    # Height for paragraph if exists
    if paragraph_text:
        para_height = estimate_text_height(paragraph_text, font_size, 12)
        total_height += para_height + 0.5  # 0.5 inches spacing after paragraph
    
    # Height for bullet points if exist
    if bullet_points:
        # Add initial spacing before bullets if there was a paragraph
        if paragraph_text:
            total_height += 0.3  # Space before bullets section
        
        # Add height for each bullet point
        for point in bullet_points:
            bullet_height = estimate_text_height(point, font_size, 11)
            total_height += bullet_height + 0.2  # 0.2 inches between bullets
    
    return total_height

def split_slide_content(paragraph_text, bullet_points, max_height=5):
    """Split content into multiple slides if needed"""
    slides_content = []
    current_para = paragraph_text
    current_bullets = bullet_points[:]
    
    while current_para or current_bullets:
        slide_content = {'paragraph': '', 'bullet_points': []}
        available_height = max_height
        
        # If we have paragraph text, try to fit it
        if current_para:
            para_height = estimate_text_height(current_para, 20, 12) + 0.5
            if para_height <= available_height:
                slide_content['paragraph'] = current_para
                available_height -= para_height
                current_para = ''  # Paragraph has been placed
            else:
                # Split paragraph if it's too long
                words = current_para.split()
                test_para = ''
                for word in words:
                    test_para_new = test_para + ' ' + word if test_para else word
                    if estimate_text_height(test_para_new, 20, 12) + 0.5 > available_height:
                        break
                    test_para = test_para_new
                
                slide_content['paragraph'] = test_para.strip()
                current_para = ' '.join(words[len(test_para.split()):]).strip()
        
        # If we have bullet points and space left, try to fit them
        if current_bullets and available_height > 0:
            if available_height >= 0.3:  # Minimum space for bullets section
                available_height -= 0.3  # Space before bullets
                
                # Try to fit as many bullets as possible
                while current_bullets:
                    bullet_height = estimate_text_height(current_bullets[0], 20, 11) + 0.2
                    if bullet_height <= available_height:
                        slide_content['bullet_points'].append(current_bullets.pop(0))
                        available_height -= bullet_height
                    else:
                        break
        
        slides_content.append(slide_content)
    
    return slides_content

def create_presentation(json_data):
    prs = Presentation()
    
    THEME_COLORS = {
        'primary': RGBColor(0, 75, 135),
        'secondary': RGBColor(240, 240, 240),
        'accent': RGBColor(255, 127, 0),
        'text': RGBColor(51, 51, 51)
    }
    
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    presentation_data = json_data.get('presentation', {})
    
    # Create title slide (same as before)
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    
    background = title_slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    apply_theme_color(background, (0, 75, 135))
    
    accent_bar = title_slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(1), Inches(3),
        Inches(2), Inches(0.1)
    )
    apply_theme_color(accent_bar, (255, 127, 0))
    
    title_box = title_slide.shapes.add_textbox(
        Inches(1), Inches(2),
        Inches(11), Inches(1)
    )
    title_frame = title_box.text_frame
    title_para = title_frame.add_paragraph()
    title_para.text = presentation_data.get('title', 'Presentation Title')
    title_para.font.size = Pt(54)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(255, 255, 255)
    title_para.alignment = PP_ALIGN.LEFT
    
    subtitle_box = title_slide.shapes.add_textbox(
        Inches(1), Inches(3.5),
        Inches(11), Inches(1)
    )
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.word_wrap = True
    subtitle_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

    subtitle_para = subtitle_frame.add_paragraph()
    subtitle_para.text = presentation_data.get('subtitle', '')
    subtitle_para.font.size = Pt(32)
    subtitle_para.font.color.rgb = RGBColor(240, 240, 240)
    subtitle_para.alignment = PP_ALIGN.LEFT
    
    # Create content slides with pagination
    slide_idx = 1
    for slide_data in presentation_data.get('slides', []):
        paragraph_text = slide_data.get('paragraph', '')
        bullet_points = slide_data.get('bullet_points', [])
        
        # Calculate total height needed
        total_height = estimate_total_height(paragraph_text, bullet_points)
        
        if total_height > 4.5:  # Maximum content height per slide
            # Split content across multiple slides
            split_contents = split_slide_content(paragraph_text, bullet_points)
            
            # Create slides for each split content
            for idx, content in enumerate(split_contents):
                is_continuation = idx > 0
                create_content_slide(
                    prs, slide_data, slide_idx, THEME_COLORS, 
                    content=content, is_continuation=is_continuation
                )
                slide_idx += 1
        else:
            # Content fits on one slide
            create_content_slide(prs, slide_data, slide_idx, THEME_COLORS)
            slide_idx += 1
    
    return prs