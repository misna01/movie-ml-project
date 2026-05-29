from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
import os
import urllib.parse
import html
import random

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

    return Response(
        svg_poster(movie_title),
        mimetype="image/svg+xml"
    )

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

        poster_url = (
            request.host_url.rstrip("/")
            + "/poster/"
            + urllib.parse.quote(movie)
        )

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
        debug=True
    )