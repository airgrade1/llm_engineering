# Import necessary libraries
import os  # For interacting with the operating system
import requests  # For making HTTP requests to fetch web content
import json  # For handling JSON data
import re
# from typing import List  # For type hints involving lists
from dotenv import load_dotenv  # For loading environment variables from a file
from bs4 import BeautifulSoup  # For parsing and extracting data from HTML
from IPython.display import Markdown, display, update_display  # For displaying Markdown in Jupyter
from openai import OpenAI  # OpenAI client for interacting with AI models
from link_developer_prompt_page import link_prompt
from developer_prompt_brochure_creator import import_developer_prompt
from user_prompt_brochure_creator import brochure_user_prompt

# Load environment variables and check for OpenAI API key
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check if API key is valid
if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print(
        "An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print(
        "An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    # print('\n')
    print("API key found and looks good so far!")

### GLOBAL VARIABLES ###

# Set the OpenAI model to use
MODEL = 'gpt-4o-mini'
# Initialize OpenAI client
openai = OpenAI()

# Define headers for HTTP requests (some websites require specific headers)
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (HTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}

# System prompt for identifying relevant links on a webpage
link_system_prompt = link_prompt

# System prompt for generating a company brochure
developer_prompt = import_developer_prompt


class Website:
    """
    Represents a website by fetching its content, title, body text, and links.
    """

    def __init__(self, url):
        """
        Initialize the Website object by fetching and parsing its content.
        :param url: The URL of the website to fetch.
        """
        self.url = url  # Store the website URL
        response = requests.get(url, headers=headers)  # Fetch the website content
        self.body = response.content  # Store the raw response content

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"  # Extract the title

        # Remove unnecessary elements like scripts, styles, images, and inputs
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)  # Extract and format the main text content
        else:
            self.text = ""

        # Extract all hyperlinks from the webpage
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]  # Remove None values

    def get_contents(self) -> str:
        """
        Returns the formatted title and content of the webpage.
        """
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


def get_company_details() -> tuple[str, str, str]:
    # Prompt user for a website name and company name
    web_name: str = input('What website to can i check>>> ')
    company_name: str = input('What is the company name? ').title()
    print(f'Creating brochure for {company_name} please be patient....')

    web = 'http'
    original_web_name = web_name  # for debugging purpose only

    if 'www' in web_name and web in web_name:  # check for https://www.email.com
        clean_url = re.sub(r"https?://www\.", "https://", web_name)
        web_name = clean_url

    elif 'www' in web_name and web not in web_name:  # check for www.email.com
        clean_url = re.sub(r"www\.", "", web_name)
        web_name = clean_url
        web_name = f'https://{web_name}'

    elif 'www' not in web_name and web not in web_name:  # check for email.com
        web_name = f'https://{web_name}'

    else:
        web_name = f'{web_name}'  # check for https://email.com

    return company_name, original_web_name, web_name


def get_links_user_prompt(website) -> str :
    """
    Generates a user prompt listing all links on a website and requesting
    identification of relevant ones for a brochure.
    """
    user_prompt = f"""Here is the list of links on the website of {website.url}. 
    Analyze the links and select the most relevant ones to include in a professional 
    brochure about the company. Prioritize links that provide essential information about the company, such as:  
    - About Us / Company Page  
    - Careers / Jobs Page  
    - Products / Services Page  
    - Contact Page  
    - News / Blog Page  

    Exclude irrelevant or overly technical links (e.g., privacy policies, login pages, or legal disclaimers). 
    Respond in JSON format, categorizing each link by type and providing the full URL.
    """
    user_prompt += "\n".join(website.links)
    return user_prompt


def get_links(url):
    """
    Fetches a website, retrieves a list of links, and uses OpenAI to determine
    which links are relevant for a company brochure.
    """
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "developer", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)  # Convert JSON string to a Python dictionary


def get_all_details(url):
    """
    Retrieves the landing page contents and extracts details from relevant links.
    """
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    # print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result


def get_brochure_user_prompt(company_name, url):
    """
    Generates a user prompt for creating a company brochure using extracted webpage content.
    """
    # create_brochure(company_name,url)
    user_prompt = brochure_user_prompt
    user_prompt += company_name
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:5_000]  # Truncate if over 5,000 characters
    return user_prompt


def create_brochure(company_name, url):
    """
    Uses OpenAI to generate a short brochure based on company details and web content.
    """
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
    )
    result = response.choices[0].message.content

    return result  # Display the generated brochure in Markdown format


def stream_brochure(company_name, url):
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
        stream=True
    )

    response = ""
    display_handle = display(Markdown(""), display_id=True)
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        response = response.replace("```", "").replace("markdown", "")
        update_display(Markdown(response), display_id=display_handle.display_id)


def main() -> None:
    company, original_web, formatted_web = get_company_details()

    # Example: Generate a brochure
    create_brochure(f"{company}", f"{formatted_web}")

    brochure_text = create_brochure(f"{company}", f"{formatted_web}")

    company_name_without_spaces = ''.join(company.split()).lower()
    file_path = f"brochure_outputs/{company_name_without_spaces}.md"
    # if os.path.exists(f"brochure_outputs/{company_name_without_spaces}.md"):
    with open(file_path, "a+") as file1:
        file1.write(brochure_text)
        file1.write(f'\n')
        file1.write(f'{original_web}\n')
        file1.write(f'\n')
        file1.write(f'{formatted_web}\n')
        file1.seek(0)
        file1_data = file1.read()
        file1.close()
        print(file1_data)
        print(f'{company} Brochure Created')


if __name__ == '__main__':
    main()
