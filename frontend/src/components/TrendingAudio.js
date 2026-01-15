import React, { useState, useEffect } from 'react';
import { getTrendingAudio } from '../api';
import { Music, TrendingUp, Play, Loader } from 'lucide-react';

function TrendingAudio() {
  const [country, setCountry] = useState('US');
  const [trendingAudio, setTrendingAudio] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const countries = [
    { code: 'US', name: 'United States' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'IN', name: 'India' },
    { code: 'CA', name: 'Canada' },
    { code: 'AU', name: 'Australia' },
    { code: 'DE', name: 'Germany' },
    { code: 'FR', name: 'France' },
    { code: 'JP', name: 'Japan' },
    { code: 'KR', name: 'South Korea' },
    { code: 'BR', name: 'Brazil' },
  ];

  useEffect(() => {
    loadTrendingAudio();
  }, [country]);

  const loadTrendingAudio = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getTrendingAudio(country, 50);
      setTrendingAudio(data);

      if (data.length === 0) {
        setError('No trending audio found. This feature may require additional configuration.');
      }
    } catch (err) {
      console.error('Error loading trending audio:', err);
      setError(
        err.response?.data?.detail ||
        'Failed to load trending audio. Make sure the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Trending Audio</h1>
        <p className="text-gray-600 mt-2">
          Discover the hottest sounds and music trending by country
        </p>
      </div>

      {/* Country Selector */}
      <div className="bg-white rounded-lg shadow p-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Country
        </label>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {countries.map((c) => (
            <button
              key={c.code}
              onClick={() => setCountry(c.code)}
              className={`px-4 py-2 rounded-lg text-sm ${
                country === c.code
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>

        {loading && (
          <div className="mt-4 flex items-center justify-center text-gray-500">
            <Loader className="w-5 h-5 animate-spin mr-2" />
            Loading trending audio for {countries.find(c => c.code === country)?.name}...
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 text-yellow-700 rounded-lg">
            {error}
          </div>
        )}
      </div>

      {/* Trending Audio List */}
      {!loading && trendingAudio.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Top {trendingAudio.length} Trending Audio - {countries.find(c => c.code === country)?.name}
          </h2>

          <div className="space-y-3">
            {trendingAudio.map((audio, index) => (
              <div
                key={audio.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  {/* Rank */}
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100 text-blue-600 font-bold">
                    {audio.rank || index + 1}
                  </div>

                  {/* Thumbnail */}
                  {audio.thumbnail && (
                    <img
                      src={audio.thumbnail}
                      alt={audio.title}
                      className="w-16 h-16 rounded-lg object-cover"
                    />
                  )}

                  {/* Info */}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 line-clamp-1">
                      {audio.title || 'Untitled'}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {audio.author || 'Unknown Artist'}
                    </p>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="text-xs text-gray-500 flex items-center gap-1">
                        <Music className="w-3 h-3" />
                        {audio.total_videos?.toLocaleString() || 0} videos
                      </span>
                      {audio.country && (
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {audio.country}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Play Button */}
                {audio.play_url && (
                  <a
                    href={audio.play_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-4 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700"
                  >
                    <Play className="w-5 h-5" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && trendingAudio.length === 0 && !error && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">
            No trending audio data available yet.
          </p>
          <p className="text-sm text-gray-400 mt-2">
            This feature is still being configured. Check back soon!
          </p>
        </div>
      )}
    </div>
  );
}

export default TrendingAudio;
