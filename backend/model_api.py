from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier


app = Flask(__name__)
CORS(app)

data = pd.read_csv("data.csv")

le_genre = LabelEncoder()
le_mood = LabelEncoder()
le_time = LabelEncoder()
le_output = LabelEncoder()

data['genre'] = le_genre.fit_transform(data['genre'])
data['mood'] = le_mood.fit_transform(data['mood'])
data['time'] = le_time.fit_transform(data['time'])
data['recommendation'] = le_output.fit_transform(data['recommendation'])

X = data[['genre', 'mood', 'time']]
y = data['recommendation']

model = DecisionTreeClassifier()
model.fit(X, y)

@app.route("/predict", methods=["POST"])
def predict():
    input_data = request.json

    test = pd.DataFrame([[
        le_genre.transform([input_data['genre']])[0],
        le_mood.transform([input_data['mood']])[0],
        le_time.transform([input_data['time']])[0]
    ]], columns=['genre', 'mood', 'time'])

    result = model.predict(test)

    return jsonify({
        "recommendation": le_output.inverse_transform(result)[0]
    })

app.run(port=5000)