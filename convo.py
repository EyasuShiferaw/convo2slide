
import logging
from scrape import scrape
from prompt import user_prompt, system_prompt
from concurrent.futures import ThreadPoolExecutor
from utility import get_completion, parse_research_data, parse_research_papers, parse_topics



# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Convo2Slide():
    def __init__(self, url) -> None:
        self.url = url 
        self.chat = []


    # def __call__(self):
    #     self.pipeline()
    #     return self.full_data
    
    
    
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
            temp = "\n".join(chat_data)
            return [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt.format(chat_data=temp)}   
                ]    
              
    def pipeline(self):
        """
        Execute the research assistance pipeline to gather and process research data.

        """

        logger.info("Executing convo2slide research) assistance pipeline.")
        
        self.chat = scrape(self.url)

        if self.chat == []:
            raise Exception("Empty list of chat messages")
            
        messages = self.construct_messages(user_prompt, system_prompt)

        if len(messages) == 0:
            raise Exception("Empty list of messages")

        response = get_completion(messages)
        print(response)

        
        
    
    url="https://chatgpt.com/share/67890791-a098-8007-be1f-a16143aa0ecb"
    convo2slide = Convo2Slide(url)
    convo2slide()

   