import requests
import json
from dotenv import load_dotenv

load_dotenv()

def generate_content(brief):
    """Auto-create text/images/video"""
    # Text generation (Free GPT-4o)
    text_response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": brief}]}
    )
    script = text_response.json()['choices'][0]['message']['content']
    
    # Image generation (Leonardo.ai)
    image_response = requests.post(
        "https://cloud.leonardo.ai/api/rest/v1/generations",
        headers={"Authorization": f"Bearer {os.getenv('LEONARDO_API_KEY')}"},
        json={"prompt": brief, "modelId": "e316348f-7773-490e-adcd-46765c32eb99"}
    )
    image_url = image_response.json()['generations_by_pk']['generated_images'][0]['url']
    
    # Video creation (Pictory.ai API simulation)
    video_id = requests.post(
        "https://api.pictory.ai/v1/videos",
        json={"script": script, "voice": "South African Male"}
    ).json()['id']
    
    return {"script": script, "image": image_url, "video_id": video_id}

# Example usage
client_brief = "Mobile app for township spaza shops inventory tracking"
print(generate_content(client_brief))
