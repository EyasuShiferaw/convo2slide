import os
import logging
from pathlib import Path
from para2pdf import create_pdf
from research_assistance import ResearchAssistance

from dotenv import load_dotenv

load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 


def main(): 

    topic = os.environ.get('topic', 'default_value')

    if topic == 'default_value' or topic == '':
        logger.error(f"Can't generate research paper report, please provide topic")
        return f"Can't generate research paper report, please provide topic"
    
    
    research_assistance = ResearchAssistance(topic)
    research_assistance_data = research_assistance()
    
    if research_assistance_data is None:
        logger.error(f"Can't generate research paper report")
       
   # Get the directory of the current script (run.py)
    script_dir = Path(__file__).parent

    # Define the path for the 'output' folder inside the script's directory
    output_dir = script_dir / 'output'
    output_dir.mkdir(exist_ok=True)  # Create 'output' directory if it doesn't exist

    # Define the file path within the 'output' directory
    output_file = str(output_dir / 'result.pdf')

    create_pdf(research_assistance_data, topic, output_file)

    logger.info(f"Successfully generated research paper report")

    
if __name__ == "__main__":
    main()    

