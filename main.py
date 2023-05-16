import os
import quart
import quart_cors
from quart import request
from hfta import run_agent
import cloudinary
import cloudinary.uploader

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# DO NOT COMMIT THIS TO GITHUB
cloudinary.config(
  cloud_name= "agent-plugin",
  api_key= "525496892125573",
  api_secret= "Z2UaRxnIldX8-_NyLCf-rdjCLfk"
)


def upload_file(file_path):
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    resource_type = 'image'
    if extension in ['.mp4', '.avi', '.mov', '.flv', '.wmv']:
        resource_type = 'video'
    elif extension in ['.wav', '.mp3', '.flac', '.aac', '.ogg']:
        resource_type = 'video'  # Cloudinary treats audio as video
    response = cloudinary.uploader.upload(file_path, resource_type=resource_type)
    return response['url']

@app.post("/agents/hfta")
async def agents_hfta():
    request_data = await quart.request.get_json(force=True)
    prompt = request_data["prompt"]
    res = run_agent(prompt)
    if res['output_type'] == 'text':
        return quart.Response(response=res['output'], status=200)
    elif res['output_type'] in ['image', 'video', 'audio']:
        url = upload_file(res['output'])
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
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
