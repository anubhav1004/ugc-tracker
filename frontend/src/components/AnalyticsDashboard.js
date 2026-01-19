import React, { useState, useEffect, useCallback, memo, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Eye, Heart, MessageCircle, Share2, Bookmark, ArrowUpDown, ArrowUp, ArrowDown, Users } from 'lucide-react';
import { useFilters } from '../FilterContext';
import AddAccountsToCollectionModal from './AddAccountsToCollectionModal';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Utility function for formatting numbers
const formatNumber = (num) => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

// Memoized MetricCard component to prevent unnecessary re-renders
const MetricCard = memo(({ title, value, subtitle, change }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
    <div className="flex justify-between items-start mb-2">
      <div>
        <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
        <p className="text-sm text-purple-600 dark:text-purple-400">{subtitle}</p>
      </div>
    </div>
    <div className="flex items-end justify-between">
      <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(value)}</p>
      {change !== undefined && change !== 0 && (
        <div className={`flex items-center text-sm ${change > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
          {change > 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
          {Math.abs(change)}%
        </div>
      )}
    </div>
  </div>
));

// Memoized ViralVideoCard component to prevent unnecessary re-renders
const ViralVideoCard = memo(({ video, rank }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-sm border border-gray-200 dark:border-gray-700 relative">
    <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">
      #{rank}
    </div>
    <div className="relative cursor-pointer group">
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
          className="opacity-0 group-hover:opacity-100 bg-white dark:bg-gray-200 rounded-full p-3 transition-all duration-200"
        >
          <svg className="w-8 h-8 text-gray-900" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
          </svg>
        </a>
      </div>
    </div>
    <div className="p-4">
      <div className="flex items-center mb-2">
        <img
          src={video.author_avatar || 'https://via.placeholder.com/40'}
          alt={video.author_username}
          className="w-8 h-8 rounded-full mr-2"
        />
        <div>
          <p className="font-semibold text-sm dark:text-white">@{video.author_username}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            uploaded on {video.posted_at ? new Date(video.posted_at).toLocaleDateString() : 'N/A'}
          </p>
        </div>
      </div>
      <p className="text-sm text-gray-700 dark:text-gray-300 mb-3 line-clamp-2">{video.caption || 'No caption'}</p>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span className="flex items-center text-gray-600 dark:text-gray-400">
            <Eye className="w-4 h-4 mr-1" /> Views
          </span>
          <span className="font-semibold dark:text-white">{formatNumber(video.views)}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="flex items-center text-gray-600 dark:text-gray-400">
            <Heart className="w-4 h-4 mr-1" /> Engagement
          </span>
          <span className="font-semibold dark:text-white">{formatNumber(video.engagement)}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="flex items-center text-gray-600 dark:text-gray-400">
            <Heart className="w-4 h-4 mr-1" /> Likes
          </span>
          <span className="font-semibold dark:text-white">{formatNumber(video.likes)}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="flex items-center text-gray-600 dark:text-gray-400">
            <MessageCircle className="w-4 h-4 mr-1" /> Comments
          </span>
          <span className="font-semibold dark:text-white">{formatNumber(video.comments)}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="flex items-center text-gray-600 dark:text-gray-400">
            <Share2 className="w-4 h-4 mr-1" /> Shares
          </span>
          <span className="font-semibold dark:text-white">{formatNumber(video.shares)}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="flex items-center text-gray-600 dark:text-gray-400">
            <Bookmark className="w-4 h-4 mr-1" /> Bookmarks
          </span>
          <span className="font-semibold dark:text-white">{formatNumber(video.bookmarks || 0)}</span>
        </div>
        <div className="flex justify-between items-center pt-2 border-t border-gray-200 dark:border-gray-700">
          <span className="text-gray-600 dark:text-gray-400">Engagement Rate</span>
          <span className="font-semibold text-purple-600 dark:text-purple-400">{video.engagement_rate}%</span>
        </div>
      </div>
    </div>
  </div>
));

function AnalyticsDashboard() {
  const { name: collectionIdFromUrl } = useParams();
  const { selectedCollection, setSelectedCollection } = useFilters();

  // Use URL param if available, otherwise use selectedCollection from context
  const activeCollectionId = collectionIdFromUrl || selectedCollection;

  // Loading state
  const [loading, setLoading] = useState(true);
  const [mixpanelLoading, setMixpanelLoading] = useState(true);

  // Consolidated data state - all API-fetched data grouped together
  const [data, setData] = useState({
    overview: null,
    viewsOverTime: [],
    mostViral: [],
    viralityAnalysis: null,
    durationAnalysis: [],
    metricsBreakdown: null,
    videoStats: [],
    analyticsData: [],
    organicOverview: null,
    adsOverview: null,
    mixpanelData: null
  });

  // Destructure for backward compatibility
  const { overview, viewsOverTime, mostViral, viralityAnalysis, durationAnalysis,
    metricsBreakdown, videoStats, analyticsData, organicOverview, adsOverview, mixpanelData } = data;

  // UI state
  const [selectedTab, setSelectedTab] = useState('Averages');
  const [metricType, setMetricType] = useState('total'); // 'total', 'organic', 'ads'

  // Video Stats sorting and filtering
  const [sortField, setSortField] = useState('views'); // 'views', 'engagement_rate', 'likes', 'comments', 'shares', 'saves'
  const [sortDirection, setSortDirection] = useState('desc'); // 'asc', 'desc'
  const [sparkAdFilter, setSparkAdFilter] = useState('all'); // 'all', 'spark_ads', 'organic'

  // Video Stats pagination
  const [displayedCount, setDisplayedCount] = useState(20);
  const [loadingMoreVideos, setLoadingMoreVideos] = useState(false);

  // Date filter state
  const [dateFilter, setDateFilter] = useState('last7days'); // 'today', 'yesterday', 'last7days', 'last30days', 'alltime', 'custom'
  const [customDateFrom, setCustomDateFrom] = useState('');
  const [customDateTo, setCustomDateTo] = useState('');
  const [showCustomDates, setShowCustomDates] = useState(false);

  // Views Over Time toggle
  const [viewMode, setViewMode] = useState('cumulative'); // 'daily' or 'cumulative'

  // Platform filter state - 'all', 'tiktok', 'instagram'
  const [selectedPlatform, setSelectedPlatform] = useState('all');

  // Collection modal state
  const [showManageAccountsModal, setShowManageAccountsModal] = useState(false);
  const [currentCollection, setCurrentCollection] = useState(null);

  // Handle platform selection
  const handlePlatformChange = (platform) => {
    setSelectedPlatform(platform);
  };

  // Calculate days based on date filter
  const getDaysForFilter = useCallback(() => {
    if (dateFilter === 'today') return 1;
    if (dateFilter === 'yesterday') return 2;
    if (dateFilter === 'last7days') return 7;
    if (dateFilter === 'last30days') return 30;
    if (dateFilter === 'alltime') return 365; // Use 365 days for all-time
    if (dateFilter === 'custom') {
      // Calculate days between custom dates
      if (customDateFrom && customDateTo) {
        const from = new Date(customDateFrom);
        const to = new Date(customDateTo);
        const diffTime = Math.abs(to - from);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays || 7;
      }
    }
    return 7; // Default
  }, [dateFilter, customDateFrom, customDateTo]);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      const days = getDaysForFilter();

      // Build platform parameter
      let platformParam = '';
      if (selectedPlatform === 'all') {
        platformParam = 'tiktok,instagram';
      } else {
        platformParam = selectedPlatform;
      }

      // Build collection parameter
      const collectionParam = activeCollectionId && activeCollectionId !== 'all' ? `&collection_id=${activeCollectionId}` : '';

      const results = await Promise.allSettled([
        axios.get(`${API_URL}/api/analytics/overview?days=${days}&metric_type=${metricType}&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/historical-growth-split?days=${days}&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/most-viral?limit=3&metric_type=${metricType}&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/virality-analysis?metric_type=${metricType}&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/duration-analysis?metric_type=${metricType}&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/metrics-breakdown?metric_type=${metricType}&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/video-stats?limit=${displayedCount}&metric_type=${metricType}&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/timeseries?days=${days}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/overview?days=${days}&metric_type=organic&platform=${platformParam}${collectionParam}`),
        axios.get(`${API_URL}/api/analytics/overview?days=${days}&metric_type=ads&platform=${platformParam}${collectionParam}`)
      ]);

      const [
        overviewRes,
        viewsRes,
        viralRes,
        viralityRes,
        durationRes,
        metricsRes,
        statsRes,
        analyticsRes,
        organicRes,
        adsRes
      ] = results.map(res => res.status === 'fulfilled' ? res.value : { data: null });

      // Update all data in one state update to reduce re-renders
      // Use functional update to preserve data that's loaded separately (like Mixpanel)
      setData(prev => ({
        ...prev,
        overview: overviewRes?.data,
        viewsOverTime: viewsRes?.data || [],
        mostViral: viralRes?.data || [],
        viralityAnalysis: viralityRes?.data,
        durationAnalysis: durationRes?.data || [],
        metricsBreakdown: metricsRes?.data,
        videoStats: statsRes?.data || [],
        analyticsData: analyticsRes?.data || [],
        organicOverview: organicRes?.data,
        adsOverview: adsRes?.data
      }));
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  }, [metricType, selectedPlatform, activeCollectionId, displayedCount, getDaysForFilter]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Lazy load Mixpanel data separately (cached for 1 hour on backend)
  const mixpanelFetchedRef = React.useRef(false);

  useEffect(() => {
    // Skip if already fetched (handles StrictMode double-mount)
    if (mixpanelFetchedRef.current) {
      return;
    }

    let isMounted = true;
    const controller = new AbortController();

    const fetchMixpanelData = async () => {
      setMixpanelLoading(true);
      try {
        const response = await axios.get(`${API_URL}/api/analytics/mixpanel`, {
          signal: controller.signal
        });
        if (isMounted) {
          setData(prev => ({ ...prev, mixpanelData: response.data }));
          mixpanelFetchedRef.current = true;
        }
      } catch (error) {
        if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
          console.error('Error fetching Mixpanel data:', error);
        }
      } finally {
        if (isMounted) {
          setMixpanelLoading(false);
        }
      }
    };

    fetchMixpanelData();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  // Sync URL param with context state
  useEffect(() => {
    if (collectionIdFromUrl && collectionIdFromUrl !== selectedCollection) {
      setSelectedCollection(collectionIdFromUrl);
    }
  }, [collectionIdFromUrl, selectedCollection, setSelectedCollection]);

  // Fetch collection details when activeCollectionId changes
  useEffect(() => {
    const fetchCollection = async () => {
      if (activeCollectionId && activeCollectionId !== 'all') {
        try {
          const response = await axios.get(`${API_URL}/api/collections/${activeCollectionId}`);
          setCurrentCollection(response.data);
        } catch (error) {
          console.error('Error fetching collection:', error);
        }
      } else {
        setCurrentCollection(null);
      }
    };
    fetchCollection();
  }, [activeCollectionId]);

  // Load more videos
  const loadMoreVideos = async () => {
    setLoadingMoreVideos(true);
    try {
      const newCount = displayedCount + 20;

      // Build platform parameter
      let platformParam = '';
      if (selectedPlatform === 'all') {
        platformParam = 'tiktok,instagram';
      } else {
        platformParam = selectedPlatform;
      }

      // Build collection parameter
      const collectionParam = activeCollectionId && activeCollectionId !== 'all' ? `&collection_id=${activeCollectionId}` : '';

      const response = await axios.get(
        `${API_URL}/api/analytics/video-stats?limit=${newCount}&metric_type=${metricType}&platform=${platformParam}${collectionParam}`
      );
      setData(prev => ({ ...prev, videoStats: response.data }));
      setDisplayedCount(newCount);
    } catch (error) {
      console.error('Error loading more videos:', error);
    } finally {
      setLoadingMoreVideos(false);
    }
  };

  // Calculate daily increments from cumulative data
  // Get the appropriate data based on view mode (memoized for performance)
  const viewsChartData = useMemo(() => {
    if (!viewsOverTime || !viewsOverTime.organic || !viewsOverTime.spark_ads) {
      return [];
    }

    const organicData = viewsOverTime.organic;
    const sparkData = viewsOverTime.spark_ads;

    if (organicData.length === 0 && sparkData.length === 0) {
      return [];
    }

    // Merge organic and spark ad data by date
    const dateMap = new Map();

    // Add organic data
    organicData.forEach(item => {
      dateMap.set(item.date, {
        date: item.date,
        organic_views: item.views_growth || 0,
        spark_views: 0
      });
    });

    // Add spark ad data
    sparkData.forEach(item => {
      if (dateMap.has(item.date)) {
        dateMap.get(item.date).spark_views = item.views_growth || 0;
      } else {
        dateMap.set(item.date, {
          date: item.date,
          organic_views: 0,
          spark_views: item.views_growth || 0
        });
      }
    });

    // Convert to array and sort by date
    const mergedData = Array.from(dateMap.values()).sort((a, b) =>
      new Date(a.date) - new Date(b.date)
    );

    if (viewMode === 'daily') {
      // Daily mode: return raw growth values
      return mergedData;
    } else {
      // Cumulative mode: calculate running totals
      let cumulativeOrganic = 0;
      let cumulativeSpark = 0;
      return mergedData.map(item => {
        cumulativeOrganic += item.organic_views;
        cumulativeSpark += item.spark_views;
        return {
          date: item.date,
          organic_views: cumulativeOrganic,
          spark_views: cumulativeSpark
        };
      });
    }
  }, [viewsOverTime, viewMode]);

  // Handle sorting for video stats
  const handleSort = (field) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to descending
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Handle filter change
  const handleFilterChange = (newFilter) => {
    setSparkAdFilter(newFilter);
  };

  // Get sorted and filtered video stats (memoized for performance)
  const sortedFilteredVideos = useMemo(() => {
    let filtered = [...videoStats];

    // Apply Spark Ads filter
    if (sparkAdFilter === 'spark_ads') {
      filtered = filtered.filter(video => video.is_spark_ad);
    } else if (sparkAdFilter === 'organic') {
      filtered = filtered.filter(video => !video.is_spark_ad);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];

      // Handle engagement_rate specially
      if (sortField === 'engagement_rate') {
        aValue = parseFloat(aValue);
        bValue = parseFloat(bValue);
      }

      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [videoStats, sparkAdFilter, sortField, sortDirection]);

  // Calculate conversion funnel data
  const getConversionFunnelData = () => {
    const totalViews = analyticsData.reduce((sum, d) => sum + d.views, 0);
    const totalInstalls = analyticsData.reduce((sum, d) => sum + d.installs, 0);
    const totalTrials = analyticsData.reduce((sum, d) => sum + d.trial_started, 0);

    return [
      { stage: 'Views', value: totalViews, fill: '#8b5cf6' },
      { stage: 'Installs', value: totalInstalls, fill: '#ec4899' },
      { stage: 'Trial Started', value: totalTrials, fill: '#10b981' }
    ];
  };

  // Get sorting icon
  const getSortIcon = (field) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-4 h-4 text-gray-400" />;
    }
    return sortDirection === 'asc'
      ? <ArrowUp className="w-4 h-4 text-purple-600 dark:text-purple-400" />
      : <ArrowDown className="w-4 h-4 text-purple-600 dark:text-purple-400" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 dark:border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {currentCollection ? `Collection: ${currentCollection.name}` : 'Comprehensive TikTok performance insights'}
          </p>
        </div>
        {currentCollection && (
          <button
            onClick={() => setShowManageAccountsModal(true)}
            className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            <Users className="w-4 h-4 mr-2" />
            Manage Accounts
          </button>
        )}
      </div>

      {/* Date Filter */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Date Range:</label>
          <div className="flex space-x-2">
            <button
              onClick={() => { setDateFilter('today'); setShowCustomDates(false); }}
              className={`px-4 py-2 text-sm rounded-lg transition ${dateFilter === 'today'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              Today
            </button>
            <button
              onClick={() => { setDateFilter('yesterday'); setShowCustomDates(false); }}
              className={`px-4 py-2 text-sm rounded-lg transition ${dateFilter === 'yesterday'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              Yesterday
            </button>
            <button
              onClick={() => { setDateFilter('last7days'); setShowCustomDates(false); }}
              className={`px-4 py-2 text-sm rounded-lg transition ${dateFilter === 'last7days'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              Last 7 Days
            </button>
            <button
              onClick={() => { setDateFilter('last30days'); setShowCustomDates(false); }}
              className={`px-4 py-2 text-sm rounded-lg transition ${dateFilter === 'last30days'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              Last 30 Days
            </button>
            <button
              onClick={() => { setDateFilter('alltime'); setShowCustomDates(false); }}
              className={`px-4 py-2 text-sm rounded-lg transition ${dateFilter === 'alltime'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              All Time
            </button>
            <button
              onClick={() => { setDateFilter('custom'); setShowCustomDates(true); }}
              className={`px-4 py-2 text-sm rounded-lg transition ${dateFilter === 'custom'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              Custom
            </button>
          </div>
        </div>

        {/* Custom Date Inputs */}
        {showCustomDates && (
          <div className="flex items-center space-x-3 mt-4">
            <label className="text-sm text-gray-600 dark:text-gray-400">From:</label>
            <input
              type="date"
              value={customDateFrom}
              onChange={(e) => setCustomDateFrom(e.target.value)}
              className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <label className="text-sm text-gray-600 dark:text-gray-400">To:</label>
            <input
              type="date"
              value={customDateTo}
              onChange={(e) => setCustomDateTo(e.target.value)}
              className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        )}
      </div>

      {/* Platform Filter */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter by Platform:</label>
          <div className="flex space-x-2">
            <button
              onClick={() => handlePlatformChange('all')}
              className={`px-4 py-2 text-sm rounded-lg transition ${selectedPlatform === 'all'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              All
            </button>
            <button
              onClick={() => handlePlatformChange('tiktok')}
              className={`px-4 py-2 text-sm rounded-lg transition ${selectedPlatform === 'tiktok'
                ? 'bg-gray-800 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              TikTok
            </button>
            <button
              onClick={() => handlePlatformChange('instagram')}
              className={`px-4 py-2 text-sm rounded-lg transition ${selectedPlatform === 'instagram'
                ? 'bg-pink-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
            >
              Instagram
            </button>
          </div>
        </div>
      </div>

      {/* Organic vs Spark Ads Comparison */}
      {organicOverview && adsOverview && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">📊 Organic vs Spark Ads Comparison</h2>
          <div className="grid grid-cols-2 gap-6">
            {/* Organic Column */}
            <div className="border-r border-gray-200 dark:border-gray-700 pr-6">
              <div className="flex items-center mb-4">
                <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                <h3 className="text-md font-semibold text-gray-900 dark:text-white">Organic (Non-Paid)</h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Views:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(organicOverview.views.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Likes:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(organicOverview.likes.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Comments:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(organicOverview.comments.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Shares:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(organicOverview.shares.total)}</span>
                </div>
              </div>
            </div>

            {/* Spark Ads Column */}
            <div className="pl-6">
              <div className="flex items-center mb-4">
                <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                <h3 className="text-md font-semibold text-gray-900 dark:text-white">Spark Ads (Paid)</h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Views:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(adsOverview.views.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Likes:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(adsOverview.likes.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Comments:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(adsOverview.comments.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Shares:</span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatNumber(adsOverview.shares.total)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Metric Type Tabs */}
      <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 mb-6">
        <button
          onClick={() => setMetricType('total')}
          className={`flex-1 px-4 py-3 rounded-md font-medium transition ${metricType === 'total'
            ? 'bg-white dark:bg-gray-700 shadow text-purple-600 dark:text-purple-400'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
        >
          <div className="text-center">
            <div className="text-lg font-bold">Total</div>
            <div className="text-xs">All Videos</div>
          </div>
        </button>
        <button
          onClick={() => setMetricType('organic')}
          className={`flex-1 px-4 py-3 rounded-md font-medium transition ${metricType === 'organic'
            ? 'bg-white dark:bg-gray-700 shadow text-green-600 dark:text-green-400'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
        >
          <div className="text-center">
            <div className="text-lg font-bold">Organic</div>
            <div className="text-xs">Non-Paid Videos</div>
          </div>
        </button>
        <button
          onClick={() => setMetricType('ads')}
          className={`flex-1 px-4 py-3 rounded-md font-medium transition ${metricType === 'ads'
            ? 'bg-white dark:bg-gray-700 shadow text-blue-600 dark:text-blue-400'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
        >
          <div className="text-center">
            <div className="text-lg font-bold">Spark Ads</div>
            <div className="text-xs">Paid Promotions</div>
          </div>
        </button>
      </div>

      {/* Metrics Cards */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          <MetricCard
            title="Views"
            value={overview.views.total}
            subtitle={
              dateFilter === 'today' ? 'Today' :
                dateFilter === 'yesterday' ? 'Yesterday' :
                  dateFilter === 'last7days' ? 'Last 7 Days' :
                    dateFilter === 'last30days' ? 'Last 30 Days' :
                      dateFilter === 'alltime' ? 'All Time' :
                        'Custom Range'
            }
          />
          <MetricCard
            title="Engagement"
            value={overview.engagement.total}
            subtitle={
              dateFilter === 'today' ? 'Today' :
                dateFilter === 'yesterday' ? 'Yesterday' :
                  dateFilter === 'last7days' ? 'Last 7 Days' :
                    dateFilter === 'last30days' ? 'Last 30 Days' :
                      dateFilter === 'alltime' ? 'All Time' :
                        'Custom Range'
            }
          />
          <MetricCard
            title="Likes"
            value={overview.likes.total}
            subtitle={
              dateFilter === 'today' ? 'Today' :
                dateFilter === 'yesterday' ? 'Yesterday' :
                  dateFilter === 'last7days' ? 'Last 7 Days' :
                    dateFilter === 'last30days' ? 'Last 30 Days' :
                      dateFilter === 'alltime' ? 'All Time' :
                        'Custom Range'
            }
          />
          <MetricCard
            title="Comments"
            value={overview.comments.total}
            subtitle={
              dateFilter === 'today' ? 'Today' :
                dateFilter === 'yesterday' ? 'Yesterday' :
                  dateFilter === 'last7days' ? 'Last 7 Days' :
                    dateFilter === 'last30days' ? 'Last 30 Days' :
                      dateFilter === 'alltime' ? 'All Time' :
                        'Custom Range'
            }
          />
          <MetricCard
            title="Shares"
            value={overview.shares.total}
            subtitle={
              dateFilter === 'today' ? 'Today' :
                dateFilter === 'yesterday' ? 'Yesterday' :
                  dateFilter === 'last7days' ? 'Last 7 Days' :
                    dateFilter === 'last30days' ? 'Last 30 Days' :
                      dateFilter === 'alltime' ? 'All Time' :
                        'Custom Range'
            }
          />
          <MetricCard
            title="Saves"
            value={overview.saves.total}
            subtitle={
              dateFilter === 'today' ? 'Today' :
                dateFilter === 'yesterday' ? 'Yesterday' :
                  dateFilter === 'last7days' ? 'Last 7 Days' :
                    dateFilter === 'last30days' ? 'Last 30 Days' :
                      dateFilter === 'alltime' ? 'All Time' :
                        'Custom Range'
            }
          />
        </div>
      )}

      {/* Views Over Time Chart */}
      {viewsChartData && viewsChartData.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div className="flex justify-between items-center mb-2">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Views Over Time</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {viewMode === 'daily'
                  ? 'Daily view growth tracked from historical snapshots'
                  : 'Cumulative views accumulated over time'}
              </p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setViewMode('daily')}
                className={`px-3 py-1 text-sm rounded transition-colors ${viewMode === 'daily'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
              >
                Daily Growth
              </button>
              <button
                onClick={() => setViewMode('cumulative')}
                className={`px-3 py-1 text-sm rounded transition-colors ${viewMode === 'cumulative'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
              >
                Cumulative
              </button>
            </div>
          </div>

          {/* Growth Rate Indicators */}
          {viewsChartData.length > 0 && (
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-purple-50 dark:bg-purple-900 rounded-lg p-4">
                <div className="text-sm text-purple-600 dark:text-purple-300 font-medium mb-1">Total Growth</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatNumber(viewsChartData.reduce((sum, item) => sum + (item.organic_views || 0) + (item.spark_views || 0), 0))}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">views gained in period</div>
              </div>
              <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-4">
                <div className="text-sm text-blue-600 dark:text-blue-300 font-medium mb-1">Daily Average</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatNumber(Math.round(viewsChartData.reduce((sum, item) => sum + (item.organic_views || 0) + (item.spark_views || 0), 0) / viewsChartData.length))}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">views per day</div>
              </div>
              <div className="bg-green-50 dark:bg-green-900 rounded-lg p-4">
                <div className="text-sm text-green-600 dark:text-green-300 font-medium mb-1">Best Day</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatNumber(Math.max(...viewsChartData.map(item => (item.organic_views || 0) + (item.spark_views || 0))))}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">highest daily growth</div>
              </div>
            </div>
          )}

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={viewsChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
              <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="organic_views"
                name="Organic Views"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="spark_views"
                name="Spark Ad Views"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Views vs Installs vs Trial Started Comparison - Removed as per user request */}
      {/* {analyticsData && analyticsData.length > 0 && (
        <div className="mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Views vs Installs vs Trial Started</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
                <XAxis
                  dataKey="date"
                  stroke="#9ca3af"
                  fontSize={12}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getMonth() + 1}/${date.getDate()}`;
                  }}
                />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip
                  labelFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                  }}
                  formatter={(value) => formatNumber(value)}
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="views" stroke="#8b5cf6" strokeWidth={2} name="Views" />
                <Line type="monotone" dataKey="installs" stroke="#ec4899" strokeWidth={2} name="Installs" />
                <Line type="monotone" dataKey="trial_started" stroke="#10b981" strokeWidth={2} name="Trial Started" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )} */}

      {/* Mixpanel Charts Section */}
      {(mixpanelLoading || mixpanelData) && (
        <div className="mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Mixpanel: Installs over Time */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Mixpanel: Installs over Time</h2>
              {mixpanelLoading ? (
                <div className="flex items-center justify-center h-[250px]">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 dark:border-purple-400 mx-auto mb-2"></div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Loading Mixpanel data...</p>
                  </div>
                </div>
              ) : mixpanelData && mixpanelData["Installs"]?.[0]?.data ? (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={mixpanelData["Installs"][0].data}>
                    <XAxis dataKey="x" stroke="#9ca3af" fontSize={11} />
                    <YAxis stroke="#9ca3af" fontSize={11} />
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: 'none',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                    />
                    <Line type="monotone" dataKey="y" stroke="#ec4899" strokeWidth={2} name="Installs" dot={true} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[250px]">
                  <p className="text-sm text-gray-500 dark:text-gray-400">No Mixpanel data available</p>
                </div>
              )}
            </div>

            {/* Mixpanel: Daily Trial Started */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Mixpanel: Daily Trial Started</h2>
              {mixpanelLoading ? (
                <div className="flex items-center justify-center h-[250px]">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 dark:border-purple-400 mx-auto mb-2"></div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Loading Mixpanel data...</p>
                  </div>
                </div>
              ) : mixpanelData && mixpanelData["Daily Trial Started"]?.[0]?.data ? (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={mixpanelData["Daily Trial Started"][0].data}>
                    <XAxis dataKey="x" stroke="#9ca3af" fontSize={11} />
                    <YAxis stroke="#9ca3af" fontSize={11} />
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: 'none',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                    />
                    <Line type="monotone" dataKey="y" stroke="#10b981" strokeWidth={2} name="Trial Started" dot={true} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[250px]">
                  <p className="text-sm text-gray-500 dark:text-gray-400">No Mixpanel data available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Conversion Funnel - Commented out as requested */}
      {/* {analyticsData && analyticsData.length > 0 && (
        <div className="mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Conversion Funnel</h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={getConversionFunnelData()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
                <XAxis dataKey="stage" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} tickFormatter={formatNumber} />
                <Tooltip
                  formatter={(value) => formatNumber(value)}
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {getConversionFunnelData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">View to Install Rate</p>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-300">
                  {getConversionFunnelData()[1]?.value && getConversionFunnelData()[0]?.value
                    ? ((getConversionFunnelData()[1].value / getConversionFunnelData()[0].value) * 100).toFixed(2)
                    : 0}%
                </p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Install to Trial Rate</p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-300">
                  {getConversionFunnelData()[2]?.value && getConversionFunnelData()[1]?.value
                    ? ((getConversionFunnelData()[2].value / getConversionFunnelData()[1].value) * 100).toFixed(2)
                    : 0}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )} */}

      {/* Most Viral Videos */}
      {mostViral && mostViral.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Most Viral Videos</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mostViral.map((video, index) => (
              <ViralVideoCard key={video.id} video={video} rank={index + 1} />
            ))}
          </div>
        </div>
      )}


      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Virality Median Analysis */}
        {viralityAnalysis && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Virality Median Analysis</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  { range: 'Below 1x', count: viralityAnalysis.below_1x },
                  { range: '1x-5x', count: viralityAnalysis['1x_to_5x'] },
                  { range: '5x-10x', count: viralityAnalysis['5x_to_10x'] },
                  { range: '10x-25x', count: viralityAnalysis['10x_to_25x'] },
                  { range: '25x-50x', count: viralityAnalysis['25x_to_50x'] },
                  { range: '50x-100x', count: viralityAnalysis['50x_to_100x'] },
                  { range: '100x+', count: viralityAnalysis.above_100x }
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="range" stroke="#9ca3af" fontSize={11} />
                <YAxis stroke="#9ca3af" fontSize={11} />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Duration Analysis */}
        {durationAnalysis && durationAnalysis.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Duration Analysis</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={durationAnalysis}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="range" stroke="#9ca3af" fontSize={11} />
                <YAxis stroke="#9ca3af" fontSize={11} />
                <Tooltip />
                <Bar dataKey="average_views" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Metrics Breakdown */}
      {metricsBreakdown && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => setSelectedTab('Averages')}
              className={`px-4 py-2 text-sm font-medium rounded ${selectedTab === 'Averages' ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'}`}
            >
              Averages
            </button>
            <button
              onClick={() => setSelectedTab('By Day')}
              className={`px-4 py-2 text-sm font-medium rounded ${selectedTab === 'By Day' ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'}`}
            >
              By Day
            </button>
            <button
              onClick={() => setSelectedTab('Upload Activity')}
              className={`px-4 py-2 text-sm font-medium rounded ${selectedTab === 'Upload Activity' ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'}`}
            >
              Upload Activity
            </button>
          </div>

          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Metrics Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Period</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Average Views</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Average Views Gain</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Average Comments Gain</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Average Likes Gain</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-100 dark:border-gray-700">
                  <td className="py-3 px-4 flex items-center">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mr-2"></div>
                    <span className="text-sm font-medium dark:text-white">Daily Average</span>
                  </td>
                  <td className="py-3 px-4 text-sm dark:text-white">
                    {formatNumber(metricsBreakdown.daily.avg_views)}
                    <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">avg views</span>
                  </td>
                  <td className="py-3 px-4 text-sm text-green-600 dark:text-green-400 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    +{formatNumber(metricsBreakdown.daily.avg_views_gain)}
                  </td>
                  <td className="py-3 px-4 text-sm text-green-600 dark:text-green-400 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    +{metricsBreakdown.daily.avg_comments_gain}
                  </td>
                  <td className="py-3 px-4 text-sm text-green-600 dark:text-green-400 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    +{formatNumber(metricsBreakdown.daily.avg_likes_gain)}
                  </td>
                </tr>
                <tr>
                  <td className="py-3 px-4 flex items-center">
                    <div className="w-2 h-2 bg-green-600 rounded-full mr-2"></div>
                    <span className="text-sm font-medium dark:text-white">Weekly Average</span>
                  </td>
                  <td className="py-3 px-4 text-sm dark:text-white">
                    {formatNumber(metricsBreakdown.weekly.avg_views)}
                    <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">avg views</span>
                  </td>
                  <td className="py-3 px-4 text-sm text-green-600 dark:text-green-400 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    +{formatNumber(metricsBreakdown.weekly.avg_views_gain)}
                  </td>
                  <td className="py-3 px-4 text-sm text-green-600 dark:text-green-400 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    +{metricsBreakdown.weekly.avg_comments_gain}
                  </td>
                  <td className="py-3 px-4 text-sm text-green-600 dark:text-green-400 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    +{formatNumber(metricsBreakdown.weekly.avg_likes_gain)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Video Stats Table */}
      {videoStats && videoStats.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          {/* Header with Filter */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Video Stats</h2>

            {/* Spark Ads Filter */}
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter:</label>
              <select
                value={sparkAdFilter}
                onChange={(e) => handleFilterChange(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="all">All Videos</option>
                <option value="spark_ads">Spark Ads Only</option>
                <option value="organic">Organic Only</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Video</th>
                  <th
                    className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400 cursor-pointer hover:text-purple-600 dark:hover:text-purple-400"
                    onClick={() => handleSort('views')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Views</span>
                      {getSortIcon('views')}
                    </div>
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Views Performance</th>
                  <th
                    className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400 cursor-pointer hover:text-purple-600 dark:hover:text-purple-400"
                    onClick={() => handleSort('engagement_rate')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Engagement Rate</span>
                      {getSortIcon('engagement_rate')}
                    </div>
                  </th>
                  <th
                    className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400 cursor-pointer hover:text-purple-600 dark:hover:text-purple-400"
                    onClick={() => handleSort('likes')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Likes</span>
                      {getSortIcon('likes')}
                    </div>
                  </th>
                  <th
                    className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400 cursor-pointer hover:text-purple-600 dark:hover:text-purple-400"
                    onClick={() => handleSort('comments')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Comments</span>
                      {getSortIcon('comments')}
                    </div>
                  </th>
                  <th
                    className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400 cursor-pointer hover:text-purple-600 dark:hover:text-purple-400"
                    onClick={() => handleSort('saves')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Saves</span>
                      {getSortIcon('saves')}
                    </div>
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Spark Ads</th>
                </tr>
              </thead>
              <tbody>
                {sortedFilteredVideos.map((video) => (
                  <tr key={video.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="py-3 px-4">
                      <div className="flex items-center">
                        <img
                          src={video.thumbnail || 'https://via.placeholder.com/60'}
                          alt={video.caption}
                          className="w-12 h-12 object-cover rounded mr-3"
                        />
                        <div className="max-w-xs">
                          <p className="text-sm font-medium dark:text-white">@{video.author_username}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{video.caption || 'No caption'}</p>
                          <p className="text-xs text-gray-400 dark:text-gray-500">
                            Uploaded on {video.posted_at ? new Date(video.posted_at).toLocaleDateString() : 'N/A'}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm">
                      <span className="bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-300 px-2 py-1 rounded font-medium">
                        {formatNumber(video.views)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${video.performance_multiplier > 1
                        ? 'bg-pink-100 dark:bg-pink-900 text-pink-800 dark:text-pink-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                        }`}>
                        {video.performance_indicator}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm font-medium dark:text-white">{video.engagement_rate}%</td>
                    <td className="py-3 px-4 text-sm dark:text-white">{formatNumber(video.likes)}</td>
                    <td className="py-3 px-4 text-sm dark:text-white">{video.comments}</td>
                    <td className="py-3 px-4 text-sm dark:text-white">{formatNumber(video.saves)}</td>
                    <td className="py-3 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${video.is_spark_ad
                        ? 'bg-pink-100 dark:bg-pink-900 text-pink-800 dark:text-pink-300 border border-pink-300 dark:border-pink-700'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                        }`}>
                        {video.is_spark_ad ? 'Yes' : 'No'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Load More Button */}
          {videoStats.length >= displayedCount && (
            <div className="flex justify-center mt-6">
              <button
                onClick={loadMoreVideos}
                disabled={loadingMoreVideos}
                className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 dark:hover:bg-purple-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingMoreVideos ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading...
                  </div>
                ) : (
                  'Load More Videos'
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Manage Accounts Modal */}
      <AddAccountsToCollectionModal
        isOpen={showManageAccountsModal}
        onClose={(shouldRefresh) => {
          setShowManageAccountsModal(false);
          if (shouldRefresh) {
            fetchAllData(); // Refresh analytics when accounts change
          }
        }}
        collection={currentCollection}
      />
    </div>
  );
}

export default AnalyticsDashboard;
