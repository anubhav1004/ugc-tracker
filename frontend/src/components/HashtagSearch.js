import React, { useState } from 'react';
import { searchHashtag, searchTerm } from '../api';
import { Search, Loader } from 'lucide-react';
import VideoCard from './VideoCard';

function HashtagSearch() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('hashtag'); // hashtag or term
  const [platform, setPlatform] = useState('tiktok');
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    setVideos([]);

    try {
      let results;
      if (searchType === 'hashtag') {
        results = await searchHashtag(query, platform, 50);
      } else {
        results = await searchTerm(query, platform, 50);
      }

      setVideos(results);

      if (results.length === 0) {
        setError('No videos found. Try a different search term or platform.');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(
        err.response?.data?.detail ||
        'Failed to search. Make sure the backend is running and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Search Videos</h1>
        <p className="text-gray-600 mt-2">
          Search for videos by hashtag or search term across platforms
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          {/* Search Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Type
            </label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setSearchType('hashtag')}
                className={`px-4 py-2 rounded-lg ${
                  searchType === 'hashtag'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Hashtag
              </button>
              <button
                type="button"
                onClick={() => setSearchType('term')}
                className={`px-4 py-2 rounded-lg ${
                  searchType === 'term'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Search Term
              </button>
            </div>
          </div>

          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Platform
            </label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setPlatform('tiktok')}
                className={`px-4 py-2 rounded-lg ${
                  platform === 'tiktok'
                    ? 'bg-black text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                TikTok
              </button>
              <button
                type="button"
                onClick={() => setPlatform('youtube')}
                className={`px-4 py-2 rounded-lg ${
                  platform === 'youtube'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                YouTube
              </button>
            </div>
          </div>

          {/* Search Input */}
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              {searchType === 'hashtag' ? 'Hashtag' : 'Search Term'}
            </label>
            <div className="flex gap-2">
              <div className="flex-1 relative">
                {searchType === 'hashtag' && (
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    #
                  </span>
                )}
                <input
                  type="text"
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={
                    searchType === 'hashtag'
                      ? 'Enter hashtag (without #)'
                      : 'Enter search term'
                  }
                  className={`w-full ${
                    searchType === 'hashtag' ? 'pl-8' : 'pl-4'
                  } pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Search
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {videos.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Found {videos.length} videos
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {videos.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default HashtagSearch;
