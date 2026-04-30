import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

# load dataset
data = pd.read_csv("data.csv")

# encoders (convert text → number)
le_genre = LabelEncoder()
le_mood = LabelEncoder()
le_time = LabelEncoder()
le_output = LabelEncoder()

data['genre'] = le_genre.fit_transform(data['genre'])
data['mood'] = le_mood.fit_transform(data['mood'])
data['time'] = le_time.fit_transform(data['time'])
data['recommendation'] = le_output.fit_transform(data['recommendation'])

# input and output
X = data[['genre', 'mood', 'time']]
y = data['recommendation']

# train model
model = DecisionTreeClassifier()
model.fit(X, y)

# user input
genre = input("Enter genre (action/comedy/romance): ")
mood = input("Enter mood (happy/sad/excited): ")
time = input("Enter time (1hr/2hr/3hr): ")

# convert input
import pandas as pd

test = pd.DataFrame([[
    le_genre.transform([genre])[0],
    le_mood.transform([mood])[0],
    le_time.transform([time])[0]
]], columns=['genre', 'mood', 'time'])

# predict
result = model.predict(test)

# show output
print("Recommended:", le_output.inverse_transform(result)[0])