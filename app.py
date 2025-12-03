import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

def text_wrap(text, font, max_width):
    """Pomožna funkcija za lomljenje teksta, če je predolg."""
    lines = []
    if font.getlength(text) <= max_width:
        lines.append(text)
    else:
        words = text.split(' ')
        i = 0
        while i < len(words):
            line = ''
            while i < len(words) and font.getlength(line + words[i]) <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line)
    return lines

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 1. Prejem podatkov
        image_file = request.files.get("image")
        top_text = request.form.get("top_text", "").upper()
        bottom_text = request.form.get("bottom_text", "").upper()

        if not image_file:
            return "Manjka slika!", 400

        # 2. Obdelava slike (Pillow)
        try:
            img = Image.open(image_file)
            
            # Pretvorba v RGB (če je slika npr. RGBA ali PNG s prosojnostjo)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            draw = ImageDraw.Draw(img)
            width, height = img.size

            # Določanje velikosti pisave glede na velikost slike
            font_size = int(height / 10)
            
            # Poskus nalaganja pisave (privzeta sistemska pisava ali fallback)
            try:
                # Za Linux/Docker okolje pogosto deluje DejaVuSans-Bold
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except IOError:
                # Fallback, če pisava ne obstaja
                font = ImageFont.load_default()

            # Pomožna funkcija za risanje teksta z obrobo (outline)
            def draw_text_with_outline(text, position, vertical_anchor):
                # Lomljenje teksta
                lines = text_wrap(text, font, width - 20)
                
                y_text = position
                for line in lines:
                    # Izračun pozicije za sredino
                    left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
                    text_width = right - left
                    text_height = bottom - top
                    
                    x_text = (width - text_width) / 2
                    
                    if vertical_anchor == 'bottom':
                         y_text -= (text_height + 10) # Premik navzgor za spodnji tekst

                    # Risanje črne obrobe
                    stroke_width = 3
                    draw.text((x_text, y_text), line, font=font, fill="white", stroke_width=stroke_width, stroke_fill="black")
                    
                    if vertical_anchor == 'top':
                        y_text += text_height + 10

            # Risanje zgornjega teksta
            if top_text:
                draw_text_with_outline(top_text, 10, 'top')

            # Risanje spodnjega teksta
            if bottom_text:
                draw_text_with_outline(bottom_text, height - 20, 'bottom')

            # 3. Priprava za vračilo (Shranjevanje v pomnilnik)
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=95)
            img_io.seek(0)

            return send_file(img_io, mimetype='image/jpeg')

        except Exception as e:
            return f"Napaka pri obdelavi: {str(e)}", 500

    return render_template("index.html")

if __name__ == "__main__":
    # Pomembno: host='0.0.0.0' omogoča dostop izven kontejnerja
    app.run(host="0.0.0.0", port=5000)