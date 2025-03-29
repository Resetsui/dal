import base64

with open("assets/images/we_profit_logo.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
    print(f"Encoded image to base64, length: {len(encoded_string)}")
    with open("logo_base64.txt", "w") as text_file:
        text_file.write(encoded_string)
    print("Base64 encoding saved to logo_base64.txt")