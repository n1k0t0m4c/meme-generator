# 1. Uporabi uradno Python osnovno sliko (slim verzija je manjša)
FROM python:3.12-slim

# 2. Nastavi delovni imenik znotraj kontejnerja
WORKDIR /app

# 3. Namestitev sistemskih knjižnic (za pisave - to je tisti "install" del v navodilih)
# Dejavu fonts namestimo, da imamo lepo pisavo za meme
RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# 4. Kopiraj requirements.txt in namesti Python odvisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kopiraj preostalo kodo aplikacije v kontejner
COPY . .

# 6. Nastavi okoljsko spremenljivko (opcijsko, a dobro za Flask)
ENV FLASK_APP=app.py

# 7. Odpri port 5000 (Flask privzeto)
EXPOSE 5000

# 8. Ukaz za zagon aplikacije
CMD ["python", "app.py"]