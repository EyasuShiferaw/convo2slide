
import logging
from prompt import user_prompt, system_prompt
from concurrent.futures import ThreadPoolExecutor
from utility import get_completion, parse_research_data, parse_research_papers, parse_topics



# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchAssistance():
    def __init__(self, url) -> None:
        self.url = url 
        self.chat = []


    def __call__(self):
        self.pipeline()
        return self.full_data
    
    
    
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
        
    def fetch_chat(self):    
            
    def pipeline(self):
        """
        Execute the research assistance pipeline to gather and process research data.
        
        This method:
        1. Gets research topics based on the main topic
        2. Fetches and parses research data for each topic in parallel
        3. Constructs messages for the API using the parsed data
        4. Gets completion from the API and parses research papers
        5. Combines the parsed data with paper metadata
        
        Returns:
            list: The processed research data, or None if there was an error
        """

        logger.info("Executing research assistance pipeline.")
        parse_data = []
        seen = set()
        id_counter = 1
       
        topics = self.get_topics()
        if topics is None:
            return None
        
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.fetch_data, topic): topic for topic in topics}
            for future in futures:
                topic = futures[future]
                try:
                    
                    result = future.result()
                    for item in result:
                       
                        key = (item["title"], tuple(item["links"]))
                        if key not in seen:
                            seen.add(key) 
                            
                            item["id"] = id_counter  
                            id_counter += 1      
                            
                            parse_data.append(item)
                except Exception as e:
                    print(f"Error processing topic '{topic}': {e}")

    
        messages = self.construct_messages(parse_data, user_prompt, system_prompt)
        if len(messages) == 0:
            return None

        response = get_completion(messages)
        self.ideas = parse_research_papers(response)
       
        for idea in (self.ideas):
            index = int(idea["id"])
            for i in parse_data:
                temp = {}
                if i["id"] == index:
                    temp = i
                    break

            idea["title"] = temp["title"]
            idea["links"] = temp["links"]
            self.full_data.append(idea)

        