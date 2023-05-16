from typing import Tuple
from transformers import OpenAiAgent
from PIL import Image
from diffusers.utils import export_to_video
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.playback import play
import soundfile as sf
import tempfile
import cv2
import torch
import imageio
import numpy as np

# Create an agent
agent = OpenAiAgent(model='gpt-4')

def export_to_gif(frames: list[np.ndarray], output_gif_path: str = None) -> str:
    if output_gif_path is None:
        output_gif_path = tempfile.NamedTemporaryFile(suffix=".gif").name

    # Convert the frames to the format expected by imageio
    frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in frames]

    # Write the frames to a GIF file
    imageio.mimsave(output_gif_path, frames, duration=1.0/8)  # duration in seconds

    return output_gif_path

def infer_output_type(output):
    if isinstance(output, str):
        return 'text'
    elif isinstance(output, Image.Image):
        return 'image'
    elif isinstance(output, list):
        return 'video'
    elif isinstance(output, torch.Tensor):
        return 'audio'
    else:
        raise ValueError("Could not infer output type from output")

def play_video(video):
    video_path = export_to_gif(video)
    # vid = VideoFileClip(video_path)
    # vid.preview()
    return video_path

def display_image(image):
    image.show()
    image.save('output.png')
    return 'output.png'

def play_audio(audio):
    sf.write("output.wav", audio.numpy(), samplerate=16000)
    audio = AudioSegment.from_file("output.wav", format="wav")
    play(audio)
    return 'output.wav'

def run_agent(prompt) -> dict:
    output = agent.run(prompt)
    # print(output)
    print(type(output))
    output_type = infer_output_type(output)
    if output_type == 'text':
        print(output)
        return {'output': output, 'output_type': output_type}
    elif output_type == 'image':
        image = display_image(output)
        return {'output': image, 'output_type': output_type}
    elif output_type == 'video':
        video = play_video(output)
        return {'output': video, 'output_type': output_type}
    elif output_type == 'audio':
        audio = play_audio(output)
        return {'output': audio, 'output_type': output_type}
    else:
        raise ValueError("Invalid output_type. Must be one of ['text', 'image', 'video', 'audio']")
    
def chat_agent(prompt) -> dict:
    output = agent.chat(prompt)
    # print(output)
    print(type(output))
    output_type = infer_output_type(output)
    if output_type == 'text':
        print(output)
        return {'output': output, 'output_type': output_type}
    elif output_type == 'image':
        image = display_image(output)
        return {'output': image, 'output_type': output_type}
    elif output_type == 'video':
        video = play_video(output)
        return {'output': video, 'output_type': output_type}
    elif output_type == 'audio':
        audio = play_audio(output)
        return {'output': audio, 'output_type': output_type}
    else:
        raise ValueError("Invalid output_type. Must be one of ['text', 'image', 'video', 'audio']")

if __name__ == '__main__':
    # text_output = run_agent("Summarize the contents of https://huggingface.co/docs/transformers/transformers_agents")
     image_output = run_agent("Show me an image of a blue frog")
     video_output = run_agent("Play a video showing a video game")
     audio_output = run_agent("say out loud something inspiring")
