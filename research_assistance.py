
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from prompt import extract_user_prompt, extract_system_prompt  ,user_prompt, system_prompt
from utility import get_completion, parse_research_data, parse_research_papers, parse_topics



# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchAssistance():
    def __init__(self, topic) -> None:
        self.topic = topic 
        self.ideas = None
        self.full_data = []


    def __call__(self):
        self.pipeline()
        return self.full_data
    
        
    def arxiv(self, topic):
       
        """
        Fetch research paper based on the topic.

        Returns:
            str: A xml format of list representing the research paper.
        """
        logger.info("Fetching research paper based on the topic.")
        if not self.topic or not isinstance(self.topic, str):
            logging.error("Given topic is not a string")
            raise ValueError("Topic must be a non-empty string")

        search_query = topic.replace(" ", "+")       
        url = f'http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results=2&order='
        response = requests.get(url)
        if response.status_code == 200: 
            return  response.content  
        else:
            logger.error(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
            return None

    
    def construct_messages(self, datas: list, user_prompt: str, system_prompt: str) -> list[dict]:
        """
        Construct the system and user prompts for the OpenAI API.
        
        Args:
            company_name (str): The name of the company.
            job_description (str): The job description.
            resume (str): The resume.
        
        Returns:
            list: A list of dictionaries representing the system and user prompts.

        """
        logger.info("Constructing messages for the API.")
        try:
            summary_list = ["\t<research_paper_summary>" + "\n" + data["title"] + data["summary"] + "</research_paper_summary>"  for data in datas]
        except:
            logging.error("Failed to parse research data - invalid dictionary format")
            return []
        else:
            temp = "\n".join(summary_list)
            return [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt.format(user_query= self.topic, research_paper_summaries=temp)}   
                ]
        

    def get_topics(self):
        
        """
        Get research topics based on the main topic.
        
        Returns:
            list: A list of related research topics.
        """
        logger.info("Getting research topics based on main topic.")
        if not self.topic or not isinstance(self.topic, str):
            logging.error("Given topic is not a string") 
            raise ValueError("Topic must be a non-empty string")
        messages = [
                    {"role": "system", "content": extract_system_prompt},
                    {"role": "user", "content": extract_user_prompt.format(user_query= self.topic)}   
                ]
        try:
            xml_topics = get_completion(messages, temp=1.0)
        except:
            logger.error("Can't generate topics from the user query")
            return None
        return parse_topics(xml_topics)


    def fetch_data(self, topic):
        """
        Fetch research paper data for a given topic from arXiv.
        
        Args:
            topic (str): The research topic to search for
            
        Returns:
            list: List of dictionaries containing parsed research paper data
        """
        logger.info(f"Fetching data for topic: {topic}")
    
        data = self.arxiv(topic)
        parse_data = parse_research_data(data)

        return parse_data
    
            
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

        