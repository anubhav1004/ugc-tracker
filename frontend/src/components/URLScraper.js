import React, { useState } from 'react';
import { Link2, Loader, Trash2, Plus } from 'lucide-react';
import axios from 'axios';
import VideoCard from './VideoCard';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function URLScraper() {
  const [urls, setUrls] = useState(['']);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addURLField = () => {
    setUrls([...urls, '']);
  };

  const removeURLField = (index) => {
    const newUrls = urls.filter((_, i) => i !== index);
    setUrls(newUrls.length > 0 ? newUrls : ['']);
  };

  const updateURL = (index, value) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleScrape = async (e) => {
    e.preventDefault();

    // Filter out empty URLs
    const validUrls = urls.filter(url => url.trim());

    if (validUrls.length === 0) {
      setError('Please enter at least one video URL');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/scrape/urls`, {
        urls: validUrls
      });

      setResults(response.data);

      if (response.data.length === 0) {
        setError('No videos could be scraped. Please check the URLs and try again.');
      }

    } catch (err) {
      console.error('Scraping error:', err);
      setError(
        err.response?.data?.detail ||
        'Failed to scrape URLs. Make sure the URLs are valid and the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setUrls(['']);
    setResults([]);
    setError('');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">URL Scraper</h1>
        <p className="text-gray-600 mt-2">
          Paste video URLs OR profile URLs to scrape metrics (views, likes, comments, shares, bookmarks, etc.)
        </p>
        <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm font-semibold text-blue-900">Supports:</p>
          <ul className="text-xs text-blue-800 mt-1 space-y-1">
            <li>• <strong>Profile URLs</strong>: Scrapes ALL videos from an account (e.g., https://www.tiktok.com/@username)</li>
            <li>• <strong>Video URLs</strong>: Scrapes a single video (e.g., https://www.tiktok.com/@username/video/123)</li>
          </ul>
        </div>
      </div>

      {/* URL Input Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleScrape} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Video URLs
            </label>

            <div className="space-y-3">
              {urls.map((url, index) => (
                <div key={index} className="flex gap-2">
                  <div className="flex-1 relative">
                    <Link2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => updateURL(index, e.target.value)}
                      placeholder="https://www.tiktok.com/@username or https://www.tiktok.com/@username/video/..."
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  {urls.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeURLField(index)}
                      className="p-3 border border-gray-300 text-gray-600 rounded-lg hover:bg-red-50 hover:text-red-600 hover:border-red-300"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            <button
              type="button"
              onClick={addURLField}
              className="mt-3 flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <Plus className="w-4 h-4" />
              Add Another URL
            </button>
          </div>

          {/* Platform Support Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-blue-900 mb-2">Supported Platforms:</p>
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="px-3 py-1 bg-black text-white text-xs rounded-full">✓ TikTok (Full Support)</span>
              <span className="px-3 py-1 bg-red-600 text-white text-xs rounded-full">YouTube (Coming Soon)</span>
              <span className="px-3 py-1 bg-pink-600 text-white text-xs rounded-full">Instagram (Coming Soon)</span>
            </div>
            <div className="text-xs text-blue-800 space-y-1">
              <p><strong>TikTok Profile:</strong> https://www.tiktok.com/@username (scrapes up to 100 videos)</p>
              <p><strong>TikTok Video:</strong> https://www.tiktok.com/@username/video/1234567890</p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Scraping... ({urls.filter(u => u.trim()).length} URLs)
                </>
              ) : (
                <>
                  <Link2 className="w-5 h-5" />
                  Scrape Videos
                </>
              )}
            </button>

            <button
              type="button"
              onClick={clearAll}
              disabled={loading}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 disabled:opacity-50"
            >
              Clear All
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Scraped {results.length} video{results.length !== 1 ? 's' : ''}
          </h2>

          {/* Aggregate Statistics */}
          {results.length > 1 && (() => {
            const totalViews = results.reduce((sum, v) => sum + v.views, 0);
            const totalLikes = results.reduce((sum, v) => sum + v.likes, 0);
            const totalComments = results.reduce((sum, v) => sum + v.comments, 0);
            const totalShares = results.reduce((sum, v) => sum + v.shares, 0);
            const totalBookmarks = results.reduce((sum, v) => sum + (v.bookmarks || 0), 0);
            const avgViews = Math.round(totalViews / results.length);
            const avgLikes = Math.round(totalLikes / results.length);
            const avgEngagement = totalViews > 0
              ? ((totalLikes + totalComments + totalShares) / totalViews * 100).toFixed(2)
              : 0;

            return (
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">📊 Aggregate Statistics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-600 uppercase">Total Views</p>
                    <p className="text-xl font-bold text-blue-600">{totalViews.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">Avg: {avgViews.toLocaleString()}</p>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-600 uppercase">Total Likes</p>
                    <p className="text-xl font-bold text-pink-600">{totalLikes.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">Avg: {avgLikes.toLocaleString()}</p>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-600 uppercase">Total Comments</p>
                    <p className="text-xl font-bold text-green-600">{totalComments.toLocaleString()}</p>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-600 uppercase">Engagement Rate</p>
                    <p className="text-xl font-bold text-purple-600">{avgEngagement}%</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-600 uppercase">Total Shares</p>
                    <p className="text-lg font-bold text-orange-600">{totalShares.toLocaleString()}</p>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-600 uppercase">Total Bookmarks</p>
                    <p className="text-lg font-bold text-yellow-600">{totalBookmarks.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            );
          })()}

          {/* Results Table */}
          <div className="overflow-x-auto mb-6">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Platform</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Author</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Views</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Likes</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Comments</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Shares</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Bookmarks</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Posted</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {results.map((video, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded font-semibold ${
                        video.platform === 'tiktok' ? 'bg-black text-white' :
                        video.platform === 'youtube' ? 'bg-red-600 text-white' :
                        video.platform === 'instagram' ? 'bg-pink-600 text-white' :
                        'bg-gray-600 text-white'
                      }`}>
                        {video.platform.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      @{video.author_username || 'unknown'}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900 font-medium">
                      {video.views.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">
                      {video.likes.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">
                      {video.comments.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">
                      {video.shares.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">
                      {video.bookmarks?.toLocaleString() || '0'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {video.posted_at ? new Date(video.posted_at).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Video Cards Grid */}
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Video Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default URLScraper;
