import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { Eye, Heart, MessageCircle, Share2, ExternalLink, Filter } from 'lucide-react';
import { useFilters } from '../FilterContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function AllVideos() {
  const location = useLocation();
  const { selectedPlatform } = useFilters();
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  // Filters
  const [filters, setFilters] = useState({
    creator: '',
    dateFrom: '',
    dateTo: '',
    isSparkAd: ''
  });
  const [creators, setCreators] = useState([]);

  useEffect(() => {
    fetchCreators();
  }, []);

  useEffect(() => {
    // Check for creator query parameter in URL
    const params = new URLSearchParams(location.search);
    const creatorParam = params.get('creator');
    if (creatorParam) {
      setFilters(prev => ({ ...prev, creator: creatorParam }));
    }
  }, [location.search]);

  useEffect(() => {
    fetchVideos(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPlatform]);

  const fetchCreators = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/creators`);
      setCreators(response.data);
    } catch (error) {
      console.error('Error fetching creators:', error);
    }
  };

  const fetchVideos = async (append = false) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }

    try {
      const params = new URLSearchParams({
        limit: 50,
        offset: append ? offset : 0
      });

      if (filters.creator) params.append('creator', filters.creator);
      if (filters.dateFrom) params.append('date_from', filters.dateFrom);
      if (filters.dateTo) params.append('date_to', filters.dateTo);
      if (filters.isSparkAd !== '') params.append('is_spark_ad', filters.isSparkAd);
      if (selectedPlatform && selectedPlatform !== 'all') params.append('platform', selectedPlatform);

      const response = await axios.get(`${API_URL}/api/videos?${params}`);

      if (append) {
        setVideos(prev => [...prev, ...response.data.videos]);
        setOffset(offset + 50);
      } else {
        setVideos(response.data.videos);
        setOffset(50);
      }

      setHasMore(response.data.has_more);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error fetching videos:', error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleApplyFilters = () => {
    setOffset(0);
    fetchVideos(false);
  };

  const handleSparkAdToggle = async (videoId, isSparkAd) => {
    try {
      await axios.patch(`${API_URL}/api/videos/${videoId}/spark-ad?is_spark_ad=${isSparkAd}`);

      // Update local state
      setVideos(videos.map(v =>
        v.id === videoId ? { ...v, is_spark_ad: isSparkAd } : v
      ));
    } catch (error) {
      console.error('Error updating Spark Ads status:', error);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 dark:border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading videos...</p>
        </div>
      </div>
    );
  }

  if (videos.length === 0 && !filters.creator && !filters.dateFrom && !filters.dateTo && filters.isSparkAd === '') {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center max-w-md">
          <Eye className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">No Videos Tracked Yet</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">Add TikTok accounts to start tracking performance analytics</p>
          <a
            href="/add-accounts"
            className="inline-flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            Add Your First Account
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">All Videos</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{total} videos total, showing {videos.length}</p>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center mb-4">
          <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Creator Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Creator</label>
            <select
              value={filters.creator}
              onChange={(e) => setFilters({ ...filters, creator: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All Creators</option>
              {creators.map(c => (
                <option key={c.username} value={c.username}>
                  {c.nickname}
                </option>
              ))}
            </select>
          </div>

          {/* Date From */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">From Date</label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Date To */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">To Date</label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Spark Ads Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Video Type</label>
            <select
              value={filters.isSparkAd}
              onChange={(e) => setFilters({ ...filters, isSparkAd: e.target.value })}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All Videos</option>
              <option value="false">Organic Only</option>
              <option value="true">Spark Ads Only</option>
            </select>
          </div>
        </div>

        <div className="mt-4 flex space-x-3">
          <button
            onClick={handleApplyFilters}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            Apply Filters
          </button>
          <button
            onClick={() => {
              setFilters({ creator: '', dateFrom: '', dateTo: '', isSparkAd: '' });
              setTimeout(() => fetchVideos(false), 0);
            }}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* No Results */}
      {videos.length === 0 && (
        <div className="text-center py-12">
          <Eye className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No videos found</h3>
          <p className="text-gray-600 dark:text-gray-400">Try adjusting your filters</p>
        </div>
      )}

      {/* Video Grid */}
      {videos.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {videos.map((video) => (
              <div
                key={video.id}
                className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
              >
                {/* Thumbnail */}
                <div className="relative group cursor-pointer">
                  <img
                    src={video.thumbnail || 'https://via.placeholder.com/300x400'}
                    alt={video.caption}
                    className="w-full h-72 object-cover"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
                    <a
                      href={video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="opacity-0 group-hover:opacity-100 bg-white rounded-full p-3 transition-all duration-200"
                    >
                      <ExternalLink className="w-6 h-6 text-gray-900" />
                    </a>
                  </div>
                  {/* Platform Badge */}
                  <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs font-medium uppercase">
                    {video.platform}
                  </div>
                  {/* Spark Ad Badge */}
                  {video.is_spark_ad && (
                    <div className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium">
                      Spark Ad
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-4">
                  {/* Author */}
                  <div className="flex items-center mb-3">
                    <img
                      src={video.author_avatar || 'https://via.placeholder.com/40'}
                      alt={video.author_username}
                      className="w-8 h-8 rounded-full mr-2"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm dark:text-white truncate">@{video.author_username}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {video.posted_at
                          ? new Date(video.posted_at).toLocaleDateString()
                          : 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Caption */}
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3 line-clamp-2 min-h-[40px]">
                    {video.caption || 'No caption'}
                  </p>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Eye className="w-3 h-3 mr-1" />
                      <span>{formatNumber(video.views)}</span>
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Heart className="w-3 h-3 mr-1" />
                      <span>{formatNumber(video.likes)}</span>
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <MessageCircle className="w-3 h-3 mr-1" />
                      <span>{formatNumber(video.comments)}</span>
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Share2 className="w-3 h-3 mr-1" />
                      <span>{formatNumber(video.shares)}</span>
                    </div>
                  </div>

                  {/* Engagement Rate */}
                  {video.views > 0 && (
                    <div className="mb-3 pb-3 border-b border-gray-200 dark:border-gray-700">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-gray-600 dark:text-gray-400">Engagement Rate</span>
                        <span className="font-semibold text-purple-600 dark:text-purple-400">
                          {(((video.likes + video.comments + video.shares) / video.views) * 100).toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Spark Ad Checkbox */}
                  <div className="flex items-center">
                    <label className="flex items-center text-sm cursor-pointer">
                      <input
                        type="checkbox"
                        checked={video.is_spark_ad || false}
                        onChange={(e) => handleSparkAdToggle(video.id, e.target.checked)}
                        className="mr-2 w-4 h-4 text-purple-600 border-gray-300 dark:border-gray-600 rounded focus:ring-purple-500"
                      />
                      <span className="text-gray-700 dark:text-gray-300">Mark as Spark Ad</span>
                    </label>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div className="flex justify-center mt-8">
              <button
                onClick={() => fetchVideos(true)}
                disabled={loadingMore}
                className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 dark:hover:bg-purple-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingMore ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading...
                  </div>
                ) : (
                  `Load More Videos (${total - videos.length} remaining)`
                )}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default AllVideos;
