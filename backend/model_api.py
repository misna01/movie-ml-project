from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
import os
import urllib.parse
import urllib.request
import urllib.error
import html
import json
import re

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "data.csv")

data = pd.read_csv(data_path)

# Normalize at load time
data["genre"] = data["genre"].str.lower().str.strip()
data["mood"]  = data["mood"].str.lower().str.strip()
data["time"]  = data["time"].str.lower().str.strip()
data["language"] = data["language"].str.lower().str.strip()

POSTER_PAGES = {
    "Mad Max Fury Road": "Mad Max: Fury Road",
    "John Wick": "John Wick (film)",
    "Avengers Endgame": "Avengers: Endgame",
    "Die Hard": "Die Hard",
    "Top Gun Maverick": "Top Gun: Maverick",
    "Mission Impossible": "Mission: Impossible (film)",
    "Logan": "Logan (film)",
    "The Dark Knight": "The Dark Knight",
    "Interstellar": "Interstellar (film)",
    "The Mask": "The Mask (1994 film)",
    "Superbad": "Superbad",
    "The Grand Budapest Hotel": "The Grand Budapest Hotel",
    "Mr Bean Movie": "Bean (film)",
    "Paddington 2": "Paddington 2",
    "The Secret Life of Walter Mitty": "The Secret Life of Walter Mitty (2013 film)",
    "Game Night": "Game Night (film)",
    "Jumanji Welcome to the Jungle": "Jumanji: Welcome to the Jungle",
    "The Nice Guys": "The Nice Guys",
    "Crazy Rich Asians": "Crazy Rich Asians (film)",
    "Titanic": "Titanic (1997 film)",
    "La La Land": "La La Land",
    "Blue Valentine": "Blue Valentine (film)",
    "The Notebook": "The Notebook (2004 film)",
    "Atonement": "Atonement (2007 film)",
    "About Time": "About Time (2013 film)",
    "The Fault in Our Stars": "The Fault in Our Stars (film)",
    "Pathaan": "Pathaan (film)",
    "Jawan": "Jawan (film)",
    "War": "War (2019 film)",
    "Sholay": "Sholay",
    "3 Idiots": "3 Idiots",
    "Hera Pheri": "Hera Pheri (2000 film)",
    "Munna Bhai MBBS": "Munna Bhai M.B.B.S.",
    "Andhadhun": "Andhadhun",
    "Dilwale Dulhania Le Jayenge": "Dilwale Dulhania Le Jayenge",
    "Kuch Kuch Hota Hai": "Kuch Kuch Hota Hai",
    "Kal Ho Naa Ho": "Kal Ho Naa Ho",
    "Devdas": "Devdas (2002 Hindi film)",
    "Jab We Met": "Jab We Met",
    "Thallumaala": "Thallumaala",
    "Minnal Murali": "Minnal Murali",
    "Lucifer": "Lucifer (2019 Indian film)",
    "Aavesham": "Aavesham (2024 film)",
    "Bheeshma Parvam": "Bheeshma Parvam",
    "Jaya Jaya Jaya Jaya Hey": "Jaya Jaya Jaya Jaya Hey",
    "Premalu": "Premalu",
    "Om Shanti Oshana": "Om Shanti Oshana",
    "Android Kunjappan Version 5.25": "Android Kunjappan Version 5.25",
    "Bangalore Days": "Bangalore Days",
    "Hridayam": "Hridayam (film)",
    "Premam": "Premam",
    "The Mummy": "The Mummy (1999 film)",
    "Guardians of the Galaxy": "Guardians of the Galaxy (film)",
    "Gladiator": "Gladiator (2000 film)",
    "The Proposal": "The Proposal (2009 film)",
    "Run": "Run (2020 American film)",
    "A Quiet Place": "A Quiet Place",
    "Inception": "Inception",
    "Knives Out": "Knives Out",
    "Source Code": "Source Code",
    "Now You See Me": "Now You See Me (film)",
    "Joker": "Joker (2019 film)",
    "Shutter Island": "Shutter Island (film)",
    "Se7en": "Seven (1995 film)",
    "Whiplash": "Whiplash (2014 film)",
    "The Social Network": "The Social Network",
    "Oppenheimer": "Oppenheimer (film)",
    "Little Miss Sunshine": "Little Miss Sunshine",
    "The Pursuit of Happyness": "The Pursuit of Happyness",
    "Forrest Gump": "Forrest Gump",
    "Manchester by the Sea": "Manchester by the Sea (film)",
    "The Green Mile": "The Green Mile (film)",
    "Schindlers List": "Schindler's List",
    "Dhoom": "Dhoom",
    "Dabangg": "Dabangg",
    "Bang Bang": "Bang Bang! (2014 film)",
    "Ghajini": "Ghajini (2008 film)",
    "Lakshya": "Lakshya (film)",
    "Delhi Belly": "Delhi Belly (film)",
    "Stree": "Stree (2018 film)",
    "Andaaz Apna Apna": "Andaz Apna Apna",
    "PK": "PK (film)",
    "Chhichhore": "Chhichhore",
    "Band Baaja Baaraat": "Band Baaja Baaraat",
    "Yeh Jawaani Hai Deewani": "Yeh Jawaani Hai Deewani",
    "Hum Tum": "Hum Tum",
    "Rocky Aur Rani Kii Prem Kahaani": "Rocky Aur Rani Kii Prem Kahaani",
    "Masaan": "Masaan",
    "Kahaani": "Kahaani",
    "Talaash": "Talaash: The Answer Lies Within",
    "Talvar": "Talvar (film)",
    "Badla": "Badla (2019 film)",
    "Special 26": "Special 26",
    "A Wednesday": "A Wednesday!",
    "Ugly": "Ugly (film)",
    "Haider": "Haider (film)",
    "Raman Raghav 2.0": "Raman Raghav 2.0",
    "Taare Zameen Par": "Taare Zameen Par",
    "Dangal": "Dangal (film)",
    "Swades": "Swades",
    "Queen": "Queen (2013 film)",
    "English Vinglish": "English Vinglish",
    "Zindagi Na Milegi Dobara": "Zindagi Na Milegi Dobara",
    "Black": "Black (2005 film)",
    "Neerja": "Neerja",
    "My Name Is Khan": "My Name Is Khan",
    "RDX": "RDX: Robert Dony Xavier",
    "Turbo": "Turbo (2024 film)",
    "Kammatti Paadam": "Kammatipaadam",
    "Malik": "Malik (film)",
    "Jan E Man": "Jan. E. Man",
    "Romancham": "Romancham",
    "Kunjiramayanam": "Kunjiramayanam",
    "Maheshinte Prathikaaram": "Maheshinte Prathikaaram",
    "Sudani from Nigeria": "Sudani from Nigeria",
    "Thattathin Marayathu": "Thattathin Marayathu",
    "Anuraga Karikkin Vellam": "Anuraga Karikkin Vellam",
    "June": "June (2019 film)",
    "Jacobinte Swargarajyam": "Jacobinte Swargarajyam",
    "Annayum Rasoolum": "Annayum Rasoolum",
    "Ennu Ninte Moideen": "Ennu Ninte Moideen",
    "Memories": "Memories (2013 film)",
    "Drishyam": "Drishyam",
    "Forensic": "Forensic (2020 film)",
    "Mumbai Police": "Mumbai Police (film)",
    "Traffic": "Traffic (2011 film)",
    "Anjaam Pathiraa": "Anjaam Pathiraa",
    "Operation Java": "Operation Java",
    "Nayattu": "Nayattu (2021 film)",
    "Iratta": "Iratta",
    "Ela Veezha Poonchira": "Ela Veezha Poonchira",
    "Charlie": "Charlie (2015 Malayalam film)",
    "Ustad Hotel": "Ustad Hotel",
    "Kumbalangi Nights": "Kumbalangi Nights",
    "Home": "Home (2021 film)",
    "North 24 Kaatham": "North 24 Kaatham",
    "1983": "1983 (film)",
    "Kaazhcha": "Kaazhcha",
    "Thanmathra": "Thanmathra",
    "Peranbu": "Peranbu",
}

POSTER_CACHE = {}
POSTER_IMAGE_URLS = {
    "Kumbalangi Nights": "https://upload.wikimedia.org/wikipedia/en/9/98/Kumbalangi_Nights_poster.jpg",
    "Talaash": "https://upload.wikimedia.org/wikipedia/en/f/f3/Talaash_poster.jpg",
    "Memories": "https://upload.wikimedia.org/wikipedia/en/1/18/Memories_%282013_film%29.jpg",
    "Forensic": "https://upload.wikimedia.org/wikipedia/en/4/4c/Forensic_film_poster.jpg",
    "Nayattu": "https://upload.wikimedia.org/wikipedia/en/7/78/Nayattu.jpg",
    "Iratta": "https://upload.wikimedia.org/wikipedia/en/0/0a/Iratta.jpg",
    "Traffic": "https://upload.wikimedia.org/wikipedia/en/5/5a/Traffic_%28Malayalam_film%29.jpg",
    "Ela Veezha Poonchira": "https://upload.wikimedia.org/wikipedia/en/8/80/Ela_Veezha_Poonchira_film_poster.jpeg",
    "Drishyam": "https://upload.wikimedia.org/wikipedia/en/9/9e/DrishyamMovie.jpg",
    "Anjaam Pathiraa": "https://upload.wikimedia.org/wikipedia/en/2/22/Anjaam_Pathiraa.jpg",
    "Operation Java": "https://upload.wikimedia.org/wikipedia/en/a/ab/Operation_java_poster.jpg",
}
REQUEST_HEADERS = {
    "User-Agent": "CinemaMatchLocal/1.0 (movie recommendation student project)"
}

def make_poster_svg(movie_title):
    palette = [
        ("#e50914", "#140000", "#f8f8f8"),
        ("#b91c1c", "#09090b", "#fee2e2"),
        ("#7f1d1d", "#18181b", "#facc15"),
        ("#991b1b", "#020617", "#bfdbfe"),
        ("#be123c", "#111827", "#f5f5f5"),
        ("#dc2626", "#1c1917", "#fde68a"),
    ]
    accent, dark, text = palette[sum(ord(ch) for ch in movie_title) % len(palette)]
    safe_title = html.escape(movie_title)
    words = safe_title.split()
    midpoint = max(1, (len(words) + 1) // 2)
    line_one = " ".join(words[:midpoint])
    line_two = " ".join(words[midpoint:])

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" viewBox="0 0 400 600">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="{accent}"/>
          <stop offset="0.48" stop-color="{dark}"/>
          <stop offset="1" stop-color="#000000"/>
        </linearGradient>
        <radialGradient id="glow" cx="50%" cy="20%" r="65%">
          <stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/>
          <stop offset="1" stop-color="#000000" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="400" height="600" fill="url(#bg)"/>
      <rect width="400" height="600" fill="url(#glow)"/>
      <g opacity="0.22">
        <rect x="22" y="26" width="32" height="548" rx="8" fill="#000000"/>
        <rect x="346" y="26" width="32" height="548" rx="8" fill="#000000"/>
        <g fill="#ffffff">
          <rect x="32" y="48" width="12" height="22" rx="2"/>
          <rect x="32" y="96" width="12" height="22" rx="2"/>
          <rect x="32" y="144" width="12" height="22" rx="2"/>
          <rect x="32" y="192" width="12" height="22" rx="2"/>
          <rect x="32" y="240" width="12" height="22" rx="2"/>
          <rect x="32" y="288" width="12" height="22" rx="2"/>
          <rect x="32" y="336" width="12" height="22" rx="2"/>
          <rect x="32" y="384" width="12" height="22" rx="2"/>
          <rect x="32" y="432" width="12" height="22" rx="2"/>
          <rect x="32" y="480" width="12" height="22" rx="2"/>
          <rect x="356" y="48" width="12" height="22" rx="2"/>
          <rect x="356" y="96" width="12" height="22" rx="2"/>
          <rect x="356" y="144" width="12" height="22" rx="2"/>
          <rect x="356" y="192" width="12" height="22" rx="2"/>
          <rect x="356" y="240" width="12" height="22" rx="2"/>
          <rect x="356" y="288" width="12" height="22" rx="2"/>
          <rect x="356" y="336" width="12" height="22" rx="2"/>
          <rect x="356" y="384" width="12" height="22" rx="2"/>
          <rect x="356" y="432" width="12" height="22" rx="2"/>
          <rect x="356" y="480" width="12" height="22" rx="2"/>
        </g>
      </g>
      <circle cx="200" cy="230" r="84" fill="#000000" opacity="0.42"/>
      <polygon points="180,185 180,275 255,230" fill="{text}" opacity="0.88"/>
      <text x="200" y="410" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="900" fill="{text}">
        <tspan x="200" dy="0">{line_one}</tspan>
        <tspan x="200" dy="42">{line_two}</tspan>
      </text>
      <text x="200" y="532" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" letter-spacing="4" fill="{text}" opacity="0.72">CINEMA MATCH</text>
    </svg>
    """
    return svg


def poster_for(movie_title, base_url):
    if movie_title in POSTER_IMAGE_URLS:
        return POSTER_IMAGE_URLS[movie_title]

    encoded_title = urllib.parse.quote(movie_title, safe="")
    return urllib.parse.urljoin(base_url, f"poster/{encoded_title}.jpg")


def fetch_url(url):
    request = urllib.request.Request(url, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(request, timeout=8) as response:
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        return response.read(), content_type


def wikipedia_api(params):
    query = urllib.parse.urlencode({**params, "format": "json", "formatversion": "2"})
    response_bytes, _ = fetch_url(f"https://en.wikipedia.org/w/api.php?{query}")
    return json.loads(response_bytes.decode("utf-8"))


def clean_wikipedia_file_name(raw_value):
    value = html.unescape(raw_value).strip()
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL).strip()
    value = re.sub(r"<.*?>", "", value).strip()

    file_match = re.search(r"\[\[\s*(?:File|Image)\s*:\s*([^|\]]+)", value, flags=re.IGNORECASE)
    if file_match:
        value = file_match.group(1)
    else:
        value = value.split("|", 1)[0].strip()

    value = value.strip("[]{} \t\r\n")
    if not value or value.lower() in {"no image.svg", "no poster available.svg"}:
        return None

    if value.lower().startswith(("file:", "image:")):
        value = value.split(":", 1)[1].strip()

    return value.replace(" ", "_")


def wikipedia_file_url(file_name):
    file_data = wikipedia_api({
        "action": "query",
        "prop": "imageinfo",
        "iiprop": "url",
        "titles": f"File:{file_name}",
    })

    pages = file_data.get("query", {}).get("pages", [])
    if not pages:
        return None

    image_info = pages[0].get("imageinfo") or []
    if not image_info:
        return None

    return image_info[0].get("url")


def wikipedia_infobox_poster_url(movie_title):
    page_title = POSTER_PAGES.get(movie_title, movie_title)
    page_data = wikipedia_api({
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": page_title,
    })

    pages = page_data.get("query", {}).get("pages", [])
    if not pages:
        return None

    revisions = pages[0].get("revisions") or []
    if not revisions:
        return None

    content = revisions[0].get("slots", {}).get("main", {}).get("content", "")
    if not content:
        return None

    for field_name in ("poster", "image"):
        match = re.search(
            rf"^\|\s*{field_name}\s*=\s*(.+)$",
            content,
            flags=re.IGNORECASE | re.MULTILINE
        )
        if not match:
            continue

        file_name = clean_wikipedia_file_name(match.group(1))
        if not file_name:
            continue

        image_url = wikipedia_file_url(file_name)
        if image_url:
            return image_url

    return None


def wikipedia_poster_url(movie_title):
    if movie_title in POSTER_IMAGE_URLS:
        return POSTER_IMAGE_URLS[movie_title]

    image_url = wikipedia_infobox_poster_url(movie_title)
    if image_url:
        return image_url

    page_title = POSTER_PAGES.get(movie_title, movie_title)
    page_slug = urllib.parse.quote(page_title.replace(" ", "_"), safe="")
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_slug}"

    summary_bytes, _ = fetch_url(summary_url)
    summary = json.loads(summary_bytes.decode("utf-8"))
    image = summary.get("thumbnail") or summary.get("originalimage") or {}
    return image.get("source")


def recommendations_for(genre, mood, time, language):
    match_steps = [
        {
            "match_type": "Exact match",
            "filters": {"genre": genre, "mood": mood, "time": time, "language": language},
        },
        {
            "match_type": "Closest mood match",
            "filters": {"genre": genre, "mood": mood, "language": language},
        },
        {
            "match_type": "Closest genre match",
            "filters": {"genre": genre, "language": language},
        },
        {
            "match_type": "Closest language match",
            "filters": {"language": language},
        },
        {
            "match_type": "Closest genre and mood match",
            "filters": {"genre": genre, "mood": mood},
        },
        {
            "match_type": "Closest genre match",
            "filters": {"genre": genre},
        },
        {
            "match_type": "Popular picks",
            "filters": {},
        },
    ]

    for step in match_steps:
        filtered = data
        for column, value in step["filters"].items():
            filtered = filtered[filtered[column] == value]

        movies = filtered["recommendation"].drop_duplicates().head(4).tolist()
        if movies:
            return movies, step["match_type"]

    return [], "No match"

@app.route("/")
def home():
    return jsonify({
        "status": "OK",
        "message": "Movie API is running",
        "total_rows": len(data)
    })

# Debug route - check what data server has
@app.route("/debug")
def debug():
    return jsonify({
        "total_rows": len(data),
        "rows": data.to_dict(orient="records")
    })


@app.route("/poster/<path:movie_file>")
def poster(movie_file):
    movie_title = urllib.parse.unquote(movie_file)
    for extension in (".svg", ".jpg", ".jpeg", ".png", ".webp"):
        if movie_title.lower().endswith(extension):
            movie_title = movie_title[: -len(extension)]
            break

    if movie_title in POSTER_CACHE:
        image_bytes, content_type = POSTER_CACHE[movie_title]
        return Response(
            image_bytes,
            mimetype=content_type,
            headers={"Cache-Control": "public, max-age=86400"}
        )

    try:
        image_url = wikipedia_poster_url(movie_title)
        if image_url:
            image_bytes, content_type = fetch_url(image_url)
            if content_type.startswith("image/"):
                POSTER_CACHE[movie_title] = (image_bytes, content_type)
                return Response(
                    image_bytes,
                    mimetype=content_type,
                    headers={"Cache-Control": "public, max-age=86400"}
                )
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
        pass

    svg = make_poster_svg(movie_title)
    return Response(
        svg,
        mimetype="image/svg+xml",
        headers={"Cache-Control": "no-store"}
    )

@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()

        if not input_data:
            return jsonify({"success": False, "error": "No input received"}), 400

        genre = input_data.get("genre", "").lower().strip()
        mood  = input_data.get("mood",  "").lower().strip()
        time  = input_data.get("time",  "").lower().strip()
        language = input_data.get("language", "english").lower().strip()

        if not genre or not mood or not time or not language:
            return jsonify({"success": False, "error": "Missing fields"}), 400

        movies_list, match_type = recommendations_for(genre, mood, time, language)

        # Return objects with mock poster URLs
        movies_data = []
        for mv in movies_list:
            movies_data.append({
                "title": mv,
                "poster": poster_for(mv, request.host_url)
            })

        return jsonify({
            "success": True,
            "matchType": match_type,
            "movies": movies_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
