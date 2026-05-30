from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
import os
import urllib.parse
import urllib.request
import urllib.error
import html
import random
import json
import re

app = Flask(__name__)
CORS(app)

# =====================================================
# LOAD DATASET
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.csv")

try:
    data = pd.read_csv(DATA_PATH)
except Exception as e:
    print(f"\n❌ ERROR LOADING CSV: {e}")
    exit()

# =====================================================
# CLEAN DATA
# =====================================================

data.columns = data.columns.str.strip().str.lower()

required_columns = [
    "genre",
    "mood",
    "time",
    "language",
    "recommendation"
]

missing = [
    col for col in required_columns
    if col not in data.columns
]

if missing:
    print(f"\n❌ Missing columns: {missing}")
    exit()

# Remove duplicate header rows
data = data[data["genre"] != "genre"]

# Normalize text
for col in ["genre", "mood", "time", "language"]:
    data[col] = (
        data[col]
        .astype(str)
        .str.lower()
        .str.strip()
    )

data["recommendation"] = (
    data["recommendation"]
    .astype(str)
    .str.strip()
)

# Remove invalid rows
data = data.dropna()
data = data[data["recommendation"] != ""]
data = data.drop_duplicates()
data = data.reset_index(drop=True)

print("\n✅ DATASET LOADED")
print("Total Movies:", len(data))
print("Genres:", sorted(data["genre"].unique()))
print("Moods:", sorted(data["mood"].unique()))
print("Times:", sorted(data["time"].unique()))
print("Languages:", sorted(data["language"].unique()))

# =====================================================
# ROTATION MEMORY
# =====================================================

ROTATION_MEMORY = {}

# =====================================================
# REAL POSTER LOOKUP
# =====================================================

POSTER_PAGES = {
    "Mad Max Fury Road": "Mad Max: Fury Road",
    "John Wick": "John Wick (film)",
    "Avengers Endgame": "Avengers: Endgame",
    "The Mummy": "The Mummy (1999 film)",
    "Top Gun Maverick": "Top Gun: Maverick",
    "Guardians of the Galaxy": "Guardians of the Galaxy (film)",
    "Logan": "Logan (film)",
    "The Dark Knight": "The Dark Knight",
    "Gladiator": "Gladiator (2000 film)",
    "Game Night": "Game Night (film)",
    "Jumanji Welcome to the Jungle": "Jumanji: Welcome to the Jungle",
    "The Nice Guys": "The Nice Guys",
    "The Mask": "The Mask (1994 film)",
    "Superbad": "Superbad",
    "The Grand Budapest Hotel": "The Grand Budapest Hotel",
    "Mr Bean Movie": "Bean (film)",
    "Paddington 2": "Paddington 2",
    "The Secret Life of Walter Mitty": "The Secret Life of Walter Mitty (2013 film)",
    "About Time": "About Time (2013 film)",
    "The Proposal": "The Proposal (2009 film)",
    "The Fault in Our Stars": "The Fault in Our Stars (film)",
    "Crazy Rich Asians": "Crazy Rich Asians (film)",
    "Titanic": "Titanic (1997 film)",
    "La La Land": "La La Land",
    "Blue Valentine": "Blue Valentine (film)",
    "The Notebook": "The Notebook (2004 film)",
    "Atonement": "Atonement (2007 film)",
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
    "Pathaan": "Pathaan (film)",
    "Jawan": "Jawan (film)",
    "Dabangg": "Dabangg",
    "War": "War (2019 film)",
    "Bang Bang": "Bang Bang! (2014 film)",
    "Ghajini": "Ghajini (2008 film)",
    "Sholay": "Sholay",
    "Lakshya": "Lakshya (film)",
    "Delhi Belly": "Delhi Belly (film)",
    "Andhadhun": "Andhadhun",
    "Stree": "Stree (2018 film)",
    "Andaaz Apna Apna": "Andaz Apna Apna",
    "3 Idiots": "3 Idiots",
    "Hera Pheri": "Hera Pheri (2000 film)",
    "Munna Bhai MBBS": "Munna Bhai M.B.B.S.",
    "PK": "PK (film)",
    "Chhichhore": "Chhichhore",
    "Band Baaja Baaraat": "Band Baaja Baaraat",
    "Jab We Met": "Jab We Met",
    "Yeh Jawaani Hai Deewani": "Yeh Jawaani Hai Deewani",
    "Hum Tum": "Hum Tum",
    "Dilwale Dulhania Le Jayenge": "Dilwale Dulhania Le Jayenge",
    "Rocky Aur Rani Kii Prem Kahaani": "Rocky Aur Rani Kii Prem Kahaani",
    "Masaan": "Masaan",
    "Kal Ho Naa Ho": "Kal Ho Naa Ho",
    "Devdas": "Devdas (2002 Hindi film)",
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
    "Thallumaala": "Thallumaala",
    "Minnal Murali": "Minnal Murali",
    "Lucifer": "Lucifer (2019 Indian film)",
    "Aavesham": "Aavesham (2024 film)",
    "RDX": "RDX: Robert Dony Xavier",
    "Turbo": "Turbo (2024 film)",
    "Kammatti Paadam": "Kammatipaadam",
    "Bheeshma Parvam": "Bheeshma Parvam",
    "Malik": "Malik (film)",
    "Jaya Jaya Jaya Jaya Hey": "Jaya Jaya Jaya Jaya Hey",
    "Jan E Man": "Jan. E. Man",
    "Romancham": "Romancham",
    "Premalu": "Premalu",
    "Om Shanti Oshana": "Om Shanti Oshana",
    "Kunjiramayanam": "Kunjiramayanam",
    "Android Kunjappan Version 5.25": "Android Kunjappan Version 5.25",
    "Maheshinte Prathikaaram": "Maheshinte Prathikaaram",
    "Sudani from Nigeria": "Sudani from Nigeria",
    "Thattathin Marayathu": "Thattathin Marayathu",
    "Anuraga Karikkin Vellam": "Anuraga Karikkin Vellam",
    "Bangalore Days": "Bangalore Days",
    "June": "June (2019 film)",
    "Hridayam": "Hridayam (film)",
    "Jacobinte Swargarajyam": "Jacobinte Swargarajyam",
    "Annayum Rasoolum": "Annayum Rasoolum",
    "Premam": "Premam",
    "Ennu Ninte Moideen": "Ennu Ninte Moideen",
    "Memories": "Memories (2013 film)",
    "Drishyam": "Drishyam",
    "Forensic": "Forensic (2020 film)",
    "Anjaam Pathiraa": "Anjaam Pathiraa",
    "Traffic": "Traffic (2011 film)",
    "Operation Java": "Operation Java",
    "Cold Case": "Cold Case (2021 film)",
    "Salute": "Salute (2022 film)",
    "Rorschach": "Rorschach (2022 film)",
    "Kuruthi": "Kuruthi (film)",
    "Appan": "Appan (film)",
    "Night Drive": "Night Drive (2022 film)",
    "Kooman": "Kooman",
    "Chaaver": "Chaaver",
    "Corona Papers": "Corona Papers",
    "Garudan": "Garudan (2023 film)",
    "2018": "2018 (film)",
    "Kurup": "Kurup (film)",
    "Christopher": "Christopher (2023 film)",
    "King of Kotha": "King of Kotha",
    "Marco": "Marco (2024 film)",
    "Odiyan": "Odiyan",
    "CBI 5": "CBI 5: The Brain",
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

POSTER_IMAGE_URLS = {
    "Memories": "https://upload.wikimedia.org/wikipedia/en/1/18/Memories_%282013_film%29.jpg",
    "Forensic": "https://upload.wikimedia.org/wikipedia/en/4/4c/Forensic_film_poster.jpg",
    "Drishyam": "https://upload.wikimedia.org/wikipedia/en/9/9e/DrishyamMovie.jpg",
    "Anjaam Pathiraa": "https://upload.wikimedia.org/wikipedia/en/2/22/Anjaam_Pathiraa.jpg",
    "Traffic": "https://upload.wikimedia.org/wikipedia/en/5/5a/Traffic_%28Malayalam_film%29.jpg",
    "Operation Java": "https://upload.wikimedia.org/wikipedia/en/a/ab/Operation_java_poster.jpg",
    "2018": "https://en.wikipedia.org/wiki/Special:Redirect/file/2018_Malayalam_film_poster.jpg",
    "Salute": "https://en.wikipedia.org/wiki/Special:Redirect/file/Salute_Malayalam_Poster.jpg",
    "Rorschach": "https://en.wikipedia.org/wiki/Special:Redirect/file/Roschach.jpeg",
    "Nayattu": "https://upload.wikimedia.org/wikipedia/en/7/78/Nayattu.jpg",
    "Iratta": "https://upload.wikimedia.org/wikipedia/en/0/0a/Iratta.jpg",
    "Ela Veezha Poonchira": "https://upload.wikimedia.org/wikipedia/en/8/80/Ela_Veezha_Poonchira_film_poster.jpeg",
    "Kumbalangi Nights": "https://upload.wikimedia.org/wikipedia/en/9/98/Kumbalangi_Nights_poster.jpg",
    "Talaash": "https://upload.wikimedia.org/wikipedia/en/f/f3/Talaash_poster.jpg",
}

POSTER_CACHE = {}
REQUEST_HEADERS = {
    "User-Agent": "CinemaMatchLocal/1.0 (movie recommendation student project)"
}


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


def poster_url_for(movie_title, base_url):
    if movie_title in POSTER_IMAGE_URLS:
        return POSTER_IMAGE_URLS[movie_title]

    return (
        base_url.rstrip("/")
        + "/poster/"
        + urllib.parse.quote(movie_title)
        + ".jpg"
    )

# =====================================================
# SIMPLE POSTER SVG
# =====================================================

def svg_poster(title):

    safe_title = html.escape(title)

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="400"
         height="600">

        <rect width="100%"
              height="100%"
              fill="#111827"/>

        <circle cx="200"
                cy="180"
                r="100"
                fill="#dc2626"
                opacity="0.5"/>

        <text x="200"
              y="380"
              fill="white"
              font-size="30"
              text-anchor="middle"
              font-family="Arial"
              font-weight="bold">

              {safe_title}

        </text>

        <text x="200"
              y="520"
              fill="white"
              font-size="18"
              text-anchor="middle"
              font-family="Arial">

              CINEMA MATCH

        </text>

    </svg>
    """

# =====================================================
# POSTER ROUTE
# =====================================================

@app.route("/poster/<path:title>")
def poster(title):

    movie_title = urllib.parse.unquote(title)

    for ext in [".jpg", ".png", ".jpeg", ".webp"]:
        if movie_title.lower().endswith(ext):
            movie_title = movie_title[:-len(ext)]

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

    return Response(svg_poster(movie_title), mimetype="image/svg+xml")

# =====================================================
# GET NEXT MOVIE
# =====================================================

def get_next_movie(
    genre,
    mood,
    time,
    language,
    exclude=None
):

    if exclude is None:
        exclude = []

    # =================================================
    # PERFECT MATCH
    # =================================================

    filtered = data[
        (data["genre"] == genre) &
        (data["mood"] == mood) &
        (data["time"] == time) &
        (data["language"] == language)
    ]

    movies = (
        filtered["recommendation"]
        .drop_duplicates()
        .tolist()
    )

    # Remove already seen movies
    movies = [
        movie for movie in movies
        if movie not in exclude
    ]

    # =================================================
    # FALLBACKS
    # =================================================

    if not movies:

        fallback = data[
            (data["genre"] == genre) &
            (data["language"] == language)
        ]

        movies = (
            fallback["recommendation"]
            .drop_duplicates()
            .tolist()
        )

        movies = [
            movie for movie in movies
            if movie not in exclude
        ]

    # =================================================
    # NO MOVIES
    # =================================================

    if not movies:
        return None

    # =================================================
    # ROTATION
    # =================================================

    key = f"{genre}|{mood}|{time}|{language}"

    if key not in ROTATION_MEMORY:
        random.shuffle(movies)
        ROTATION_MEMORY[key] = {
            "movies": movies,
            "index": 0
        }

    memory = ROTATION_MEMORY[key]

    # rebuild if movie count changed
    if set(memory["movies"]) != set(movies):
        random.shuffle(movies)
        memory["movies"] = movies
        memory["index"] = 0

    index = memory["index"]

    # reset rotation
    if index >= len(memory["movies"]):
        random.shuffle(memory["movies"])
        memory["index"] = 0
        index = 0

    selected_movie = memory["movies"][index]

    memory["index"] += 1

    return selected_movie

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "Cinema Match Backend Running",
        "total_movies": len(data)
    })

# =====================================================
# OPTIONS
# =====================================================

@app.route("/options")
def options():

    return jsonify({

        "genres":
            sorted(data["genre"].unique().tolist()),

        "moods":
            sorted(data["mood"].unique().tolist()),

        "times":
            sorted(data["time"].unique().tolist()),

        "languages":
            sorted(data["language"].unique().tolist())
    })

# =====================================================
# DEBUG
# =====================================================

@app.route("/debug")
def debug():

    return jsonify({

        "total_rows": len(data),

        "sample_movies":
            data.head(20).to_dict(orient="records")
    })

# =====================================================
# TEST ROUTE
# =====================================================

@app.route("/test")
def test():

    filtered = data[
        (data["genre"] == "romance")
    ]

    return jsonify({

        "count": len(filtered),

        "movies":
            filtered["recommendation"].tolist()
    })

# =====================================================
# PREDICT
# =====================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        body = request.get_json(silent=True)

        if not body:

            return jsonify({

                "success": False,
                "movies": [],
                "error": "No JSON body received"

            }), 200

        genre = (
            str(body.get("genre", ""))
            .lower()
            .strip()
        )

        mood = (
            str(body.get("mood", ""))
            .lower()
            .strip()
        )

        time = (
            str(body.get("time", ""))
            .lower()
            .strip()
        )

        language = (
            str(body.get("language", ""))
            .lower()
            .strip()
        )

        exclude = body.get("exclude", [])

        # =============================================
        # VALIDATION
        # =============================================

        missing = []

        if not genre:
            missing.append("genre")

        if not mood:
            missing.append("mood")

        if not time:
            missing.append("time")

        if not language:
            missing.append("language")

        if missing:

            return jsonify({

                "success": False,
                "movies": [],
                "error":
                    f"Missing fields: {', '.join(missing)}"

            }), 200

        # =============================================
        # GET MOVIE
        # =============================================

        movie = get_next_movie(
            genre,
            mood,
            time,
            language,
            exclude
        )

        # =============================================
        # NO MOVIE FOUND
        # =============================================

        if not movie:

            return jsonify({

                "success": False,
                "movies": [],
                "error":
                    "No movies found for selected filters"

            }), 200

        # =============================================
        # POSTER URL
        # =============================================

        poster_url = poster_url_for(movie, request.host_url)

        movie_data = {
            "title": movie,
            "poster": poster_url
        }

        # =============================================
        # SUCCESS RESPONSE
        # =============================================

        return jsonify({

            "success": True,

            "movie": movie_data,

            "movies": [movie_data],

            "totalResults": 1,

            "selectedFilters": {

                "genre": genre,
                "mood": mood,
                "time": time,
                "language": language
            }
        })

    except Exception as e:

        print("\n❌ PREDICT ERROR")
        print(str(e))

        return jsonify({

            "success": False,
            "movies": [],
            "error": str(e)

        }), 200

# =====================================================
# RESET ROTATION
# =====================================================

@app.route("/reset", methods=["POST"])
def reset():

    ROTATION_MEMORY.clear()

    return jsonify({

        "success": True,
        "message": "Rotation memory cleared"
    })

# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    print(f"\n🚀 Server Running On Port {port}\n")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
