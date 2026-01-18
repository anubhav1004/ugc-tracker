import React, { useState } from 'react';
import axios from 'axios';
import { Plus, X, Sparkles, TrendingUp, Users } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function AddAccounts() {
  const [urls, setUrls] = useState(['']);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const addUrlField = () => {
    setUrls([...urls, '']);
  };

  const removeUrlField = (index) => {
    const newUrls = urls.filter((_, i) => i !== index);
    setUrls(newUrls.length === 0 ? [''] : newUrls);
  };

  const updateUrl = (index, value) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleAddAccounts = async () => {
    const validUrls = urls.filter((url) => url.trim() !== '');

    if (validUrls.length === 0) {
      setError('Please enter at least one username or link');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await axios.post(`${API_URL}/api/scrape/urls`, {
        urls: validUrls,
      });

      // Backend now returns immediately with status "processing"
      // Show success message and redirect
      alert(`Scraping started for ${validUrls.length} account(s)! This may take a few minutes. Check "All Accounts" page to see when it's complete.`);
      setUrls(['']);

      // Redirect to All Accounts page after 2 seconds
      setTimeout(() => {
        window.location.href = '/all-accounts';
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add accounts. Please try again.');
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-2">
          <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg mr-3">
            <Plus className="w-6 h-6 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Add Accounts</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Track TikTok & Instagram accounts and get instant analytics
            </p>
          </div>
        </div>
      </div>

      {/* Main Card */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 mb-6">
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
            TikTok & Instagram Accounts
          </label>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Enter usernames or paste full links - both work! (TikTok default, use "instagram:username" for Instagram)
          </p>

          {/* URL Input Fields */}
          <div className="space-y-3">
            {urls.map((url, index) => (
              <div key={index} className="flex items-center space-x-3">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => updateUrl(index, e.target.value)}
                  placeholder={index === 0 ? "username or @username or https://www.tiktok.com/@username" : "instagram:username or https://www.instagram.com/username/"}
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
                {urls.length > 1 && (
                  <button
                    onClick={() => removeUrlField(index)}
                    className="p-3 text-gray-400 dark:text-gray-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Add Another Link Button */}
          <button
            onClick={addUrlField}
            className="mt-3 flex items-center text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add another link
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Add Button */}
        <button
          onClick={handleAddAccounts}
          disabled={loading}
          className="w-full px-6 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold text-lg flex items-center justify-center"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
              Adding Accounts...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 mr-2" />
              Add to Dashboard
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Successfully Added</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {results.length} {results.length === 1 ? 'video' : 'videos'} added to your dashboard
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-green-100 rounded-full">
                <svg
                  className="w-5 h-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Results Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {results.map((video) => (
              <div
                key={video.id}
                className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
              >
                <img
                  src={video.thumbnail || 'https://via.placeholder.com/80'}
                  alt={video.caption}
                  className="w-20 h-20 object-cover rounded-lg"
                />
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                    @{video.author_username}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
                    {video.caption || 'No caption'}
                  </p>
                  <div className="flex items-center space-x-3 text-xs text-gray-500 dark:text-gray-400">
                    <span>{formatNumber(video.views)} views</span>
                    <span>•</span>
                    <span>{formatNumber(video.likes)} likes</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* View Dashboard Link */}
          <div className="mt-6 text-center">
            <a
              href="/"
              className="inline-flex items-center px-6 py-3 bg-gray-900 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              <TrendingUp className="w-5 h-5 mr-2" />
              View Analytics Dashboard
            </a>
          </div>
        </div>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900 dark:to-blue-900 rounded-xl p-6 border border-purple-100 dark:border-purple-800">
          <div className="p-2 bg-white dark:bg-gray-800 rounded-lg inline-block mb-3">
            <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Instant Analytics</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Get real-time performance metrics for every video you track
          </p>
        </div>

        <div className="bg-gradient-to-br from-pink-50 to-purple-50 dark:from-pink-900 dark:to-purple-900 rounded-xl p-6 border border-pink-100 dark:border-pink-800">
          <div className="p-2 bg-white dark:bg-gray-800 rounded-lg inline-block mb-3">
            <TrendingUp className="w-5 h-5 text-pink-600 dark:text-pink-400" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Performance Tracking</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Monitor views, engagement, and virality metrics over time
          </p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900 dark:to-cyan-900 rounded-xl p-6 border border-blue-100 dark:border-blue-800">
          <div className="p-2 bg-white dark:bg-gray-800 rounded-lg inline-block mb-3">
            <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Compare Creators</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Analyze multiple accounts and identify top performers
          </p>
        </div>
      </div>

      {/* Pro Tips */}
      <div className="mt-8 bg-gray-900 text-white rounded-xl p-6">
        <h3 className="font-semibold text-lg mb-3">💡 Pro Tips</h3>
        <ul className="space-y-2 text-sm opacity-90">
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span>
              <strong>Quick Entry:</strong> Just type a username (e.g., "karissa.curious") - it defaults to TikTok. For Instagram, use "instagram:username"
            </span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span>
              <strong>Track Competitors:</strong> Add TikTok and Instagram links to benchmark performance across platforms
            </span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span>
              <strong>Find Trends:</strong> Monitor viral content on both TikTok and Instagram to discover trending formats
            </span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span>
              <strong>Multi-Platform Tracking:</strong> Compare performance across TikTok and Instagram in one dashboard
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default AddAccounts;
