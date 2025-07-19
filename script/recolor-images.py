import os
import base64
import openai
import requests
from pathlib import Path

openai.api_key = os.getenv("OPENAI_API_KEY")

view_files = {
    "front": "rockpigeon-exterior-front-porch.jpg",
    "back": "rockpigeon-exterior-back-porch-wide.jpg",
    "full": "rockpigeon-exterior-full.jpg"
}

# Output dir
output_dir = Path("recolor_outputs")
output_dir.mkdir(exist_ok=True)

# HOA palette definitions
palettes = [
    ("01", "Sage", "2860", "Creamy", "7010"),
    ("02", "At Ease Soldier", "9127", "Eaglet Beige", "7573"),
    # ... add others as needed
]

# Build base64 data from image
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Prompt construction
def make_prompt(view, main_color, main_code, trim_color, trim_code):
    return (
        f"Recolor this house photo taken from the {view} to reflect a new exterior paint scheme. "
        f"Use Sherwin-Williams '{main_color}' (SW {main_code}) for the main siding and "
        f"'{trim_color}' (SW {trim_code}) for the trim (including fascia, window trim, and door frames). "
        "Maintain realistic lighting, texture, and shadows. Do not alter unpainted features such as the roof, sky, concrete, stonework, plants, or windows. "
        "This should look like a convincing real-world repaint of the same house."
    )

# Main loop
for pid, main, main_code, trim, trim_code in palettes:
    for view, view_path in view_files.items():
        image_data = encode_image(view_path)
        prompt = make_prompt(view, main, main_code, trim, trim_code)
        print(f"🔧 Processing Palette {pid} - View {view}")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]}
                ]
            )

            image_url = response['choices'][0]['message']['content']
            img_data = requests.get(image_url).content

            output_path = output_dir / f"palette{pid}-{view}.jpg"
            with open(output_path, "wb") as f:
                f.write(img_data)

        except Exception as e:
            print(f"❌ Failed on {pid} - {view}: {e}")
