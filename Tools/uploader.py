import os
import requests
import base64
from dotenv import load_dotenv
load_dotenv()


def upload_img(image_path, api_key=os.getenv('IMGBB_API_KEY')):
    """
    Upload an image file to ImgBB. The API key is taken from the `api_key` param
    or the `IMGBB_API_KEY` environment variable.

    Returns the uploaded image URL on success or raises an exception on failure.
    """
    if api_key is None:
        api_key = os.getenv('IMGBB_API_KEY')

    if not api_key:
        raise RuntimeError('ImgBB API key not provided (set IMGBB_API_KEY)')

    url = "https://api.imgbb.com/1/upload"

    # ImgBB accepts 'image' as base64 string or multipart file. We'll send base64
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')

    payload = {
        'key': api_key,
        'image': b64
    }

    response = requests.post(url, data=payload, timeout=30)

    try:
        data = response.json()
    except Exception:
        response.raise_for_status()

    if response.status_code == 200 and data.get('success'):
        print('UPLOAD_SUCCESS:', data['data']['url'])
        return data['data']['url']
    else:
        # Provide a clearer error message for logs/diagnosis
        err = data.get('error') if isinstance(data, dict) else None
        msg = f"Error: {response.status_code} - {response.text}"
        if err and isinstance(err, dict):
            msg = f"Error: {response.status_code} - {err.get('message')} (code {err.get('code')})"
        raise RuntimeError(msg)

