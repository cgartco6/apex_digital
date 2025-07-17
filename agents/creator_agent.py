import os
import openai
from dotenv import load_dotenv
import requests

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class CreatorAgent:
    def generate_text(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_image(self, prompt):
        # Using Leonardo.ai - example with their API (check their docs for exact endpoint)
        # Note: Leonardo has a free tier with limited tokens
        headers = {
            "Authorization": f"Bearer {os.getenv('LEONARDO_API_KEY')}"
        }
        data = {
            "prompt": prompt,
            "modelId": "e316348f-7773-490e-adcd-46765c32eb99",  # example model, choose one
            "width": 512,
            "height": 512
        }
        response = requests.post("https://cloud.leonardo.ai/api/rest/v1/generations", json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get('generated_images', [])[0].get('url')
        else:
            return None

    # Similarly for video (using Suno.ai or other) and audio.
