import requests

def upload_image_to_imgbb(api_key, image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    # Define the endpoint and parameters
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": api_key,
        "image": encoded_image
    }

    # Make the request
    response = requests.post(url, data=payload)

    # Check the response status
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Example usage
if __name__ == "__main__":
    api_key = "52db6f6e9307700bed6a053af81fa41b"
    image_path = "generated_image.png"
    try:
        result = upload_image_to_imgbb(api_key, image_path)
        print("Image uploaded successfully:")
        print("URL:", result["data"]["url"])
    except Exception as e:
        print(e)
