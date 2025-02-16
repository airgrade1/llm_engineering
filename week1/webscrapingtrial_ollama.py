import os              # Provides functions to interact with the operating system
from pyexpat.errors import messages

import requests        # For sending HTTP requests
from dotenv import load_dotenv  # For loading environment variables from a .env file
from bs4 import BeautifulSoup   # For parsing HTML content
from IPython.display import Markdown, display  # For displaying output in Jupyter as Markdown
from openai import OpenAI      # Importing the OpenAI client
import ollama


# Load environment variables from a file named .env
load_dotenv(override=True)

# Retrieve api-key

ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# HEADERS = {"Content-Type": "application/json"}
# MODEL = "llama3.2"


# Headers to use for certain websites that require a custom User-Agent
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (HTML, like Gecko) "
               "Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    """
    Represents a website with a URL, a title, and text content.
    Uses BeautifulSoup to parse the HTML and extract relevant text.
    """
    def __init__(self, url):
        self.url = url
        # Send a GET request using custom headers
        response = requests.get(url, headers=headers)
        # Parse the HTML response
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract the title if it exists, otherwise provide a default
        self.title = soup.title.string if soup.title else "No title found"
        # Remove irrelevant elements to avoid clutter in the text
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        # Extract the remaining body text
        self.text = soup.body.get_text(separator="\n", strip=True)

# Prompt user for a website name
web_name: str = input('What website to can i check>>> ')
web = 'http'

if 'www' in web_name and web not in web_name:
    strip_www = web_name.rstrip('www')
    web_name = f'https://{web_name}'
if 'www' not in web_name and web not in web_name:
    web_name = f'https://{web_name}'
if 'www' in web_name:
    strip_www = web_name.rstrip('www')
    web_name = f'{web_name}'
else:
    web_name = f'{web_name}'
# Instantiate the Website class using the input URL
ed = Website(f'{web_name}')

# Print the title and text extracted from the website
print(f'{web_name} title: {ed.title}\n')
# print(f'{web_name} content: \n {ed.text}')

# Define a system prompt describing how the AI should respond
system_prompt = (
    "You are an assistant that analyzes the contents of a website "
    "and provides a short summary, ignoring text that might be navigation related. "
    # "Respond in markdown."
)

def user_prompt_for(website):
    """
    Creates a user prompt that includes the website's title and text,
    requesting a short summary of the site's content in markdown format.
    """
    user_prompt = f"""You are looking at a website titled {website.title}"
    "\nThe contents of this website is as follows; "
    "please provide a short summary of this website. "
     "If it includes news or announcements, then summarize these too.\n\n"""
    user_prompt += website.text
    return user_prompt

# Print the user prompt for demonstration
# print(user_prompt_for(ed))

def messages_for(website):
    """
    Returns a list of messages for the OpenAI chat API, including
    both system and user prompts.
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

# View the messages that will be sent to the model
messages_for(ed)

def summarize(url):
    """
    Creates a Website object from the given URL, constructs the messages,
    and calls the OpenAI API to get a summary of the website.
    """
    website = Website(url)
    response = ollama_via_openai.chat.completions.create(
        model="llama3.2",
        messages=messages_for(website)
    )
    return response.choices[0].message.content

# Request and print a summary of the entered website
# AI building its logic
summarize(f"{web_name}")


def display_summary(url):
    """
    Generates a summary of the website at the specified URL and
    displays it as markdown in the Jupyter output.
    """
    summary = summarize(url)
    return summary

# Display the summary for the user-provided website
summary_text: str = display_summary(f"{web_name}")
print(summary_text)

with open("webscrape.txt","a") as file1:
    file1.write(web_name)
    file1.write(f'\n')
    file1.write(ed.title)
    # file1.write(f'\n')
    # file1.write(ed.text)
    file1.write(f'\n')
    file1.write(summary_text)
    file1.write(f'\n')
