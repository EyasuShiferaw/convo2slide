import logging
from scrape import scrape_chat_messages
from prompt import extract_note_system_prompt, extract_note_user_prompt, slide_system_prompt, slide_user_prompt
from utility import get_completion, parse_topics



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

    
    def construct_messages(self, name: str, value: str, user_prompt: str, system_prompt: str) -> list[dict]:
        """
        Construct the system and user prompts for the OpenAI API.
        
        Returns:
            list: A list of dictionaries representing the system and user prompts.
        """
        logger.info("Constructing messages for the API.")
       
        return [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt.format(name=value)}   
                ]   
        
    def generate_note(self):

        try:
            chat_data = [f"{message['role'].capitalize()}:  {message['content']}" for message in self.chat]
        except:
            logging.error("Failed to parse chat data - invalid dictionary format)")
            return []
        else:
            temp = "\n".join(chat_data)
            message = self.construct_messages("chat_data", chat_data, extract_note_user_prompt, extract_note_system_prompt )
        

              
    def pipeline(self):
        """
        Execute the research assistance pipeline to gather and process research data.

        """

        logger.info("Executing convo2slide research) assistance pipeline.")
        
        self.chat = scrape_chat_messages(self.url)



        if self.chat == []:
            raise Exception("Empty list of chat messages")
            return None
            
        messages = self.construct_messages(user_prompt, system_prompt)

        if len(messages) == 0:
            raise Exception("Empty list of messages")
            return None

        response = get_completion(messages)
        title, subtitle, slides_data = parse_topics(response)
        return title, subtitle, slides_data
    