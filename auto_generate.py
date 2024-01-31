from urllib import request
from openai import OpenAI
from PIL import Image
import glob
import json
import random
import os
import asyncio
import yaml


# Queue a new prompt to comfyui
async def queue_prompt(prompt):
    print("Queuing prompt...")
    for key in prompt.keys():
        if prompt[key]["_meta"]["title"] == "input_pose": # Get a random openpose from /poses folder
            prompt[key]["inputs"]["image"] = choose_random_file(os.getcwd() + "/poses/")
        elif prompt[key]["_meta"]["title"] == "positive_prompt": # Get a positive prompt for clothes from gpt
            gpt_res = await chat_with_gpt(gpt_pos_prompt) 
            prompt[key]["inputs"]["text"] = base_pos_prompt + gpt_res
        elif prompt[key]["_meta"]["title"] == "negative_prompt": 
            prompt[key]["inputs"]["text"] = base_neg_prompt
        elif prompt[key]["_meta"]["title"] == "save_image":
            prompt[key]["inputs"]["output_path"] = os.getcwd() + "/result/"

    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)

# Get a random file from a directory
def choose_random_file(directory_path):
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    if not files: 
        return None
    return random.choice(files)

# Get a chatgpt prompt based on base_prompt
async def chat_with_gpt(gpt_prompt):
    client = OpenAI(api_key=gpt_api_key)
    chat_completion = client.chat.completions.create( messages=[{"role": "user", "content": gpt_prompt,}], model="gpt-3.5-turbo",)
    return chat_completion.choices[0].message.content

# Remove metadata (exif) from image
def remove_meta_data(image_name):
    image = Image.open(os.getcwd() + "/result/" + image_name)
    data = list(image.getdata())
    image2 = Image.new(image.mode, image.size)
    image2.putdata(data)
    image2.save(os.getcwd() + "/final/" + image_name)

# Get the latest image generated
def get_latest_image_path():
    pattern = os.getcwd() + "/result/ComfyUI_*.png"
    file_list = sorted(glob.glob(pattern)) # Get the list of all matching files and sort them
    return file_list[-1] if file_list else None

#===================================================================================================

with open("secret.yaml", "r") as file:
	config = yaml.safe_load(file)

with open("final_api.json", "r") as f:
    j = json.load(f)

gpt_pos_prompt = "Write an original and uncommon description of a photo posted by a beautiful european woman with brown hairs, instagram influencer. Describe every clothes she is wearing, the background, the face emotions (smiling, crying, etc), etc using adjectives and short descriptions. In your answer, only write up to 50 words without repetition, separated by comma and nothing else. Make sure to be original in the description and to think out of the box."
gpt_neg_prompt = ""
base_pos_prompt = "18 year old, eastern Europe, dark brown hair, dark eyes, "
base_neg_prompt = "bad anatomy, bad hands, three hands, three legs, bad arms, missing legs, missing arms, poorly drawn face, bad face, fused face, cloned face, worst face, three crus, extra crus, fused crus, worst feet, three feet, fused feet, fused thigh, three thigh, fused thigh, extra thigh, worst thigh, missing fingers, extra fingers, ugly fingers, long fingers, horn, extra eyes, huge eyes, 2girl, amputation, disconnected limbs, cartoon, cg, 3d, unreal, animate, (watermark:1.2), (text:1.2), logo, (3D render:1.2), drawing, painting, crayon, bug, malformation, bad proportions, (mole:1.1), (bad hands:1.15), perfect, magazine, professional model, tattoos, (too many fingers:1.15)"
gpt_api_key = config['openai_api_key']
drive_api_key = config['drive_api_key']

asyncio.run(queue_prompt(j))
