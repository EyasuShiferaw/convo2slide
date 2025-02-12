import os
import logging
from pathlib import Path
from convo import Convo2Slide
from utility import create_presentation

from dotenv import load_dotenv

load_dotenv()

 
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 


def main(): 

    # Get the directory of the current script (run.py)
    script_dir = Path(__file__).parent

    # Define the path for the 'output' folder inside the script's directory
    output_dir = script_dir / 'output'
    output_dir.mkdir(exist_ok=True)  # Create 'output' directory if it doesn't exist

    url = os.environ.get('url', 'default_value')
    if url == 'default_value' or url == '':
        logger.error(f"Can't generate power point from the given url.)")
        return f"Can't generate power point from the given url."
    
    
    convo2slide = Convo2Slide(url)
  
    try: 
        slides_data = convo2slide.pipeline()
    except:
        output_file = str(output_dir / 'result.txt')
        with open(output_file, 'w') as f:
            f.write("Can't generate slides from the given url.")
        raise Exception("Can't generate slides from the given url.")
    
    # Define the file path within the 'output' directory
    output_file = str(output_dir / 'result.pptx')

   
    presentation = create_presentation(slides_data)
    presentation.save(output_file)

    logger.info("Successfully generated the power point presentation.)")

    
if __name__ == "__main__":
    main()    

