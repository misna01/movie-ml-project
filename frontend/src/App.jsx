import { useState } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Film, Clock, Smile, Languages, Search, AlertCircle, PlayCircle } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:10000";

const backdropTiles = [
  { title: "Mad Max", tone: "from-red-700 to-zinc-950" },
  { title: "John Wick", tone: "from-zinc-700 to-black" },
  { title: "Endgame", tone: "from-red-900 to-purple-950" },
  { title: "Dark Knight", tone: "from-neutral-700 to-black" },
  { title: "Interstellar", tone: "from-blue-950 to-black" },
  { title: "Titanic", tone: "from-sky-900 to-zinc-950" },
  { title: "3 Idiots", tone: "from-amber-700 to-red-950" },
  { title: "Pathaan", tone: "from-red-800 to-black" },
  { title: "Jawan", tone: "from-stone-700 to-red-950" },
  { title: "Minnal Murali", tone: "from-red-800 to-black" },
  { title: "Premalu", tone: "from-fuchsia-900 to-zinc-950" },
  { title: "Bangalore Days", tone: "from-orange-800 to-black" }
];

const posterFallback = (title) =>
  `${API_BASE_URL}/poster/${encodeURIComponent(title)}.jpg`;

function App() {
  const [genre, setGenre] = useState("action");
  const [mood, setMood] = useState("excited");
  const [time, setTime] = useState("2hr");
  const [language, setLanguage] = useState("english");
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMovies([]);
    setHasSearched(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/predict`, {
        genre,
        mood,
        time,
        language
      });

      if (res.data.success && res.data.movies) {
        setMovies(res.data.movies);
      } else {
        setError("Invalid response format from server.");
      }
    } catch (err) {
      console.error(err);
      const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
      if (isLocal) {
        setError("Error connecting to backend. Make sure your local Flask server is running on port 10000.");
      } else {
        setError(
          "Error connecting to backend. Note: Render's free tier backend service spins down after inactivity and can take 50+ seconds to boot up on the first request. If this persists, make sure the VITE_API_BASE_URL environment variable is configured in Render."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 1, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  const isLocalhost = typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");
  const isApiLocal = API_BASE_URL.includes("localhost") || API_BASE_URL.includes("127.0.0.1");
  const isMisconfiguredProduction = !isLocalhost && isApiLocal;

  return (
    <div className="min-h-screen font-sans text-white bg-[#00040a] overflow-hidden relative selection:bg-blue-600 selection:text-white">
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div 
          className="absolute inset-0 opacity-85 bg-[url('/movie_posters_bg.png')] bg-cover bg-center z-0"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#000a1f]/60 via-[#000a1f]/75 to-[#000208]/90 z-10" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(20,50,229,0.25),transparent_45%),linear-gradient(90deg,rgba(0,0,0,0.7),rgba(0,0,0,0.1),rgba(0,0,0,0.7))] z-10" />
      </div>

      <div className="max-w-6xl mx-auto px-6 py-12 relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center p-3 bg-red-600 rounded-2xl backdrop-blur-md mb-4 border border-red-400/30 shadow-xl shadow-red-950/60">
            <Film className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white drop-shadow-[0_8px_30px_rgba(0,0,0,0.9)]">
            Cinema Match
          </h1>
          <p className="mt-4 text-zinc-200 text-lg md:text-xl font-medium max-w-2xl mx-auto">
            Discover the perfect movie for your current vibe. Choose your preferences and let our engine decide your fate.
          </p>
        </motion.div>

        {isMisconfiguredProduction && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto bg-amber-950/85 border border-amber-500/40 text-amber-200 p-5 rounded-2xl flex flex-col md:flex-row items-center gap-4 mb-10 backdrop-blur-2xl shadow-xl shadow-amber-950/40"
          >
            <AlertCircle className="w-10 h-10 text-amber-400 shrink-0" />
            <div className="text-sm text-center md:text-left">
              <h4 className="font-bold text-base text-amber-100 mb-1">⚠️ Warning: Deployed site is pointing to a local backend</h4>
              <p>
                Your frontend is deployed, but it is trying to connect to a local server (<code className="bg-amber-900/50 px-1.5 py-0.5 rounded text-amber-300 font-mono">http://127.0.0.1:10000</code>). 
                To make this app work for others, please deploy your Python backend on Render and configure the <code className="bg-amber-900/50 px-1.5 py-0.5 rounded text-amber-300 font-mono">VITE_API_BASE_URL</code> environment variable in your Render dashboard.
              </p>
            </div>
          </motion.div>
        )}

        <motion.div 
          initial={{ opacity: 1, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-black/65 backdrop-blur-2xl border border-white/15 p-6 md:p-8 rounded-2xl shadow-2xl shadow-black/70 max-w-4xl mx-auto mb-16"
        >
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Genre */}
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-zinc-300 uppercase tracking-wider ml-1">
                <Film className="w-4 h-4 text-red-400" /> Genre
              </label>
              <div className="relative">
                <select
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  className="w-full appearance-none bg-zinc-950/70 border border-zinc-700 text-white p-4 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none transition-all cursor-pointer hover:bg-zinc-900/80"
                >
                  <option value="action">Action</option>
                  <option value="comedy">Comedy</option>
                  <option value="romance">Romance</option>
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-zinc-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/></svg>
                </div>
              </div>
            </div>

            {/* Mood */}
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-zinc-300 uppercase tracking-wider ml-1">
                <Smile className="w-4 h-4 text-amber-400" /> Mood
              </label>
              <div className="relative">
                <select
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
                  className="w-full appearance-none bg-zinc-950/70 border border-zinc-700 text-white p-4 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none transition-all cursor-pointer hover:bg-zinc-900/80"
                >
                  <option value="excited">Excited</option>
                  <option value="happy">Happy</option>
                  <option value="sad">Sad</option>
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-zinc-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/></svg>
                </div>
              </div>
            </div>

            {/* Time */}
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-zinc-300 uppercase tracking-wider ml-1">
                <Clock className="w-4 h-4 text-blue-400" /> Time
              </label>
              <div className="relative">
                <select
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="w-full appearance-none bg-zinc-950/70 border border-zinc-700 text-white p-4 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none transition-all cursor-pointer hover:bg-zinc-900/80"
                >
                  <option value="1hr">1 Hour</option>
                  <option value="2hr">2 Hours</option>
                  <option value="3hr">3 Hours</option>
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-zinc-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/></svg>
                </div>
              </div>
            </div>

            {/* Language */}
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-zinc-300 uppercase tracking-wider ml-1">
                <Languages className="w-4 h-4 text-green-400" /> Language
              </label>
              <div className="relative">
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full appearance-none bg-zinc-950/70 border border-zinc-700 text-white p-4 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none transition-all cursor-pointer hover:bg-zinc-900/80"
                >
                  <option value="english">English</option>
                  <option value="hindi">Hindi</option>
                  <option value="malayalam">Malayalam</option>
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-zinc-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/></svg>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="lg:col-span-4 flex justify-center mt-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={loading}
                className="w-full md:w-auto px-10 py-4 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl shadow-lg shadow-red-950/60 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Find Recommendations
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>

        {/* Results Section */}
        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="max-w-xl mx-auto bg-red-950/70 border border-red-500/40 text-red-100 p-4 rounded-xl flex items-center gap-3 justify-center mb-10 backdrop-blur-xl"
            >
              <AlertCircle className="w-5 h-5" />
              <p>{error}</p>
            </motion.div>
          )}

          {!loading && hasSearched && !error && movies.length === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-20"
            >
              <div className="inline-flex bg-black/70 p-6 rounded-full mb-4 border border-zinc-700">
                <Film className="w-12 h-12 text-zinc-500" />
              </div>
              <h3 className="text-2xl font-bold text-zinc-100">No match found</h3>
              <p className="text-zinc-400 mt-2">Try tweaking your vibe or language filters.</p>
            </motion.div>
          )}

          {!loading && !error && movies.length > 0 && (
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="show"
              className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 gap-y-12"
            >
              {movies.map((movie, idx) => (
                <motion.div
                  key={idx}
                  variants={itemVariants}
                  whileHover={{ y: -10 }}
                  className="group relative cursor-pointer"
                >
                  <div className="relative aspect-[2/3] rounded-xl overflow-hidden shadow-2xl bg-zinc-900 transition-all duration-300 group-hover:shadow-red-600/30 ring-1 ring-white/10">
                    <img 
                      src={movie.poster} 
                      alt={movie.title}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                      loading="lazy"
                      onError={(e) => {
                        e.currentTarget.src = posterFallback(movie.title);
                      }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent opacity-75 group-hover:opacity-90 transition-opacity duration-300" />
                    
                    <div className="absolute inset-x-0 bottom-0 p-6 translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                      <div className="w-10 h-10 rounded-full bg-red-600 flex items-center justify-center mb-4 opacity-0 group-hover:opacity-100 shadow-lg shadow-red-950/60 transition-opacity duration-300 delay-100">
                        <PlayCircle className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-xl font-bold text-white tracking-wide">{movie.title}</h3>
                      <div className="flex gap-2 items-center mt-2">
                        <span className="text-xs font-semibold text-red-100 bg-red-600/60 px-2 py-1 rounded border border-red-400/30 capitalize">{genre}</span>
                        <span className="text-xs font-medium text-zinc-300 capitalize">{language}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
