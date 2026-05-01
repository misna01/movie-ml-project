import { useState } from "react";
import axios from "axios";

function App() {
  const [genre, setGenre] = useState("action");
  const [mood, setMood] = useState("happy");
  const [time, setTime] = useState("2hr");
  const [result, setResult] = useState("");

  const handleSubmit = async () => {
    try {
const res = await axios.post("https://movie-ml-project.onrender.com/predict", {        genre,
        mood,
        time
      });
      setResult(res.data.recommendation);
    } catch (err) {
      console.error(err);
      setResult("Error connecting to backend");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-pink-500 to-indigo-600 animate-gradient">

      <div className="bg-white/10 backdrop-blur-lg p-8 rounded-2xl shadow-2xl w-[350px] text-center text-white">

        <h1 className="text-2xl font-bold mb-6 animate-pulse">
          🎬 Movie Recommender
        </h1>

        {/* Genre */}
        <div className="mb-4">
          <label className="block mb-1">Genre</label>
          <select
            className="w-full p-2 rounded-lg text-black"
            onChange={(e) => setGenre(e.target.value)}
          >
            <option value="action">Action</option>
            <option value="comedy">Comedy</option>
            <option value="romance">Romance</option>
          </select>
        </div>

        {/* Mood */}
        <div className="mb-4">
          <label className="block mb-1">Mood</label>
          <select
            className="w-full p-2 rounded-lg text-black"
            onChange={(e) => setMood(e.target.value)}
          >
            <option value="happy">Happy</option>
            <option value="sad">Sad</option>
            <option value="excited">Excited</option>
          </select>
        </div>

        {/* Time */}
        <div className="mb-6">
          <label className="block mb-1">Time</label>
          <select
            className="w-full p-2 rounded-lg text-black"
            onChange={(e) => setTime(e.target.value)}
          >
            <option value="1hr">1 Hour</option>
            <option value="2hr">2 Hours</option>
            <option value="3hr">3 Hours</option>
          </select>
        </div>

        {/* Button */}
        <button
          onClick={handleSubmit}
          className="w-full bg-white text-purple-600 font-bold py-2 rounded-lg hover:scale-105 transition duration-300 shadow-lg"
        >
          Get Recommendation
        </button>

        {/* Result */}
        {result && (
          <div className="mt-6 p-3 bg-white/20 rounded-lg animate-fade-in">
            <p className="font-semibold">🎯 {result}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;