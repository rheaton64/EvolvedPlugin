import os
import quart
import quart_cors
from quart import request
from hfta import run_agent
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import requests
import argparse

load_dotenv()
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

def upload_file(file_path, is_direct_link=False):
    if is_direct_link:
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        resource_type = 'image'
        if extension in ['.mp4', '.avi', '.mov', '.flv', '.wmv']:
            resource_type = 'video'
        elif extension in ['.wav', '.mp3', '.flac', '.aac', '.ogg']:
            resource_type = 'video'  # Cloudinary treats audio as video
        response = cloudinary.uploader.upload(file_path, resource_type=resource_type)
        return response['url']
    else:
        with open(file_path, 'rb') as file:
            server_response = requests.get('https://api.gofile.io/getServer')
            server = server_response.json()['data']['server']
            upload_response = requests.post(
                f'https://{server}.gofile.io/uploadFile',
                files={'file': file}
            )
            if upload_response.ok:
                return upload_response.json()['data']['downloadPage']

@app.post("/agents/hfta")
async def agents_hfta():
    global is_direct_link
    request_data = await quart.request.get_json(force=True)
    prompt = request_data["prompt"]
    res = run_agent(prompt)
    if res['output_type'] == 'text':
        return quart.Response(response=res['output'], status=200)
    elif res['output_type'] in ['image', 'video', 'audio']:
        url = upload_file(res['output'], is_direct_link=is_direct_link)
        return quart.jsonify({'url': url})

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--direct', action='store_true', help='Set is_direct_link to True')
    args = parser.parse_args()

    global is_direct_link
    is_direct_link = args.direct

    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
