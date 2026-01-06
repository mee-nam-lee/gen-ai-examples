import requests
import os
import json
import base64
import google.auth
import google.auth.transport.requests

def generate_image_rest():
    # Get application default credentials
    credentials, project_id = google.auth.default()
    
    # Refresh credentials to get an access token
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token

    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/gemini-2.5-flash-image:generateContent"
    #url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/gemini-3-pro-image-preview:generateContent"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # The request body provided by the user
    data = {
      "contents": [
        {
          "role": "user",
          "parts": [
            {
              "text": "Create a futuristic cityscape at night with neon lights, flying cars, and towering skyscrapers in cyberpunk style"
            }
          ]
        }
      ],
      "generationConfig": {
        #"temperature": 1
        #,"maxOutputTokens": 32768,
        "responseModalities": ["IMAGE"]
        #,"topP": 0.95
        ,"imageConfig": {
            "aspectRatio": "16:9"
            #,"imageSize": "1K"
            #,"imageOutputOptions": {
            #    "mimeType": "image/png"
            #}
            #,"personGeneration": "ALLOW_ALL"
        }
    },
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        
        response_json = response.json()
        
        # Optional: Save image if the response contains image data
        if "candidates" in response_json:
            print ("candidates")
            for i, candidate in enumerate(response_json["candidates"]):
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part and "mimeType" in part["inlineData"] and "data" in part["inlineData"]:
                            mime_type = part["inlineData"]["mimeType"]
                            base64_data = part["inlineData"]["data"]
                            
                            # Determine file extension
                            if "png" in mime_type:
                                ext = "png"
                            elif "jpeg" in mime_type:
                                ext = "jpeg"
                            elif "webp" in mime_type:
                                ext = "webp"
                            else:
                                print(f"Warning: Unknown mime type {mime_type}. Skipping image save.")
                                continue
                            
                            filename = f"generated_image_{i}.{ext}"
                            with open(filename, "wb") as f:
                                f.write(base64.b64decode(base64_data))
                            print(f"Image saved as {filename}")

    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        if hasattr(err, 'response') and err.response is not None:
            print(f"Response body: {err.response.text}")

generate_image_rest()
