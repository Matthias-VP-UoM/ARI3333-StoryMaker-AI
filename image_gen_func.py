from huggingface_hub import InferenceClient
import configparser
import re
import requests
import ollama
from PIL import Image

def load_image_model():
    # Load or create the configuration file
    config = configparser.ConfigParser()

    try:
        config.read("config.ini")
        api_key = config.get("HuggingFace", "api_key")
    except (configparser.NoSectionError, configparser.NoOptionError):
        api_key = None

    client = InferenceClient("black-forest-labs/FLUX.1-dev", token=api_key)

    return client

def generate_images(prompt, client):
    image = client.text_to_image(prompt)
    
    return image


def generate_image_prompts(paras_dict):
    images_prompt = f"""
    From each extracted part, generate a short but effective prompt of around 20 to 30 words which could be used to generate an image
    visualising the context of each part, ensuring that each prompt is written between inverted commas (""):
    """

    for element, para in paras_dict.items():
        images_prompt += f"\n{element.capitalize()}\n{para}\n"
    
    response = ollama.chat(
        model='llama3.2',
        messages=[
            {"role": "user", "content": images_prompt}
        ]
    )

    return response['message']['content']

def generate_image_prompts_2(story_text):
    images_prompt = f"""
    From the given story below, generate 3 short but effective prompts of around 20 to 30 words which could be used to generate an image
    visualising the context of each part, ensuring that each prompt is written between inverted commas (""). The three prompts should focus 
    on the beginning, climax and end of the story: 
    {story_text}
    """
    
    response = ollama.chat(
        model='llama3.2',
        messages=[
            {"role": "user", "content": images_prompt}
        ]
    )

    return response['message']['content']


def extract_image_prompts(prompts_text):
    # Regular expression to match text within double quotes
    matches = re.findall(r'"(.*?)"', prompts_text, re.DOTALL)

    # Print the extracted sentences
    return matches

