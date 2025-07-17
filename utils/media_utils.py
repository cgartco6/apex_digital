import requests
import os
import subprocess
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip

def generate_ai_image(prompt, output_path, service='leonardo'):
    """Generate image using AI services"""
    if service == 'leonardo':
        headers = {"Authorization": f"Bearer {os.getenv('LEONARDO_API_KEY')}"}
        payload = {
            "prompt": prompt,
            "modelId": "e316348f-7773-490e-adcd-46765c32eb99",
            "width": 1024,
            "height": 768
        }
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            image_url = response.json().get('generated_images', [{}])[0].get('url')
            if image_url:
                img_data = requests.get(image_url).content
                with open(output_path, 'wb') as f:
                    f.write(img_data)
                return output_path
    
    return None

def create_slideshow_video(images, audio_path, output_path, duration_per_image=5):
    """Create video from images and audio"""
    clips = []
    for img in images:
        img_clip = ImageSequenceClip([img], durations=[duration_per_image])
        clips.append(img_clip)
    
    final_clip = concatenate_videoclips(clips)
    audio_clip = AudioFileClip(audio_path)
    final_clip = final_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, fps=24)
    return output_path

def generate_ai_voice(text, output_path, voice='south_african_male'):
    """Generate voiceover using ElevenLabs"""
    headers = {
        "xi-api-key": os.getenv('ELEVENLABS_API_KEY'),
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    return None

def compress_media(file_path, max_size_mb=10):
    """Compress media files for web"""
    if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        img = Image.open(file_path)
        img.save(file_path, optimize=True, quality=85)
    elif file_path.endswith('.mp4'):
        cmd = f"ffmpeg -i {file_path} -vcodec libx265 -crf 28 {file_path}_compressed.mp4"
        subprocess.run(cmd, shell=True)
        return f"{file_path}_compressed.mp4"
    return file_path
