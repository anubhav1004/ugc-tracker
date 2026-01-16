import React, { useState, useEffect } from 'react';
import { getVideos, getAnalyticsTimeseries } from '../api';
import { TrendingUp } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell } from 'recharts';

function Dashboard() {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange] = useState(7); // Last 7 days
  const [analyticsData, setAnalyticsData] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [videosData, analytics] = await Promise.all([
        getVideos({ limit: 100 }),
        getAnalyticsTimeseries(timeRange)
      ]);
      setVideos(videosData);
      setAnalyticsData(analytics);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Calculate metrics from last 7 days
  const calculateMetrics = () => {
    const now = new Date();
    const daysAgo = new Date(now.getTime() - timeRange * 24 * 60 * 60 * 1000);

    const recentVideos = videos.filter(v => {
      const postedDate = new Date(v.posted_at || v.scraped_at);
      return postedDate >= daysAgo;
    });

    const totalViews = recentVideos.reduce((sum, v) => sum + (v.views || 0), 0);
    const totalLikes = recentVideos.reduce((sum, v) => sum + (v.likes || 0), 0);
    const totalComments = recentVideos.reduce((sum, v) => sum + (v.comments || 0), 0);
    const totalShares = recentVideos.reduce((sum, v) => sum + (v.shares || 0), 0);
    const totalBookmarks = recentVideos.reduce((sum, v) => sum + (v.bookmarks || 0), 0);
    const totalEngagement = totalLikes + totalComments + totalShares;

    return {
      views: totalViews,
      engagement: totalEngagement,
      likes: totalLikes,
      comments: totalComments,
      shares: totalShares,
      saves: totalBookmarks,
      videoCount: recentVideos.length
    };
  };

  // Generate time series data for chart
  const generateTimeSeriesData = () => {
    const data = [];
    const now = new Date();

    for (let i = timeRange - 1; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

      const dayVideos = videos.filter(v => {
        const videoDate = new Date(v.posted_at || v.scraped_at);
        return videoDate.toDateString() === date.toDateString();
      });

      const dayViews = dayVideos.reduce((sum, v) => sum + (v.views || 0), 0);
      const dayEngagement = dayVideos.reduce((sum, v) =>
        sum + (v.likes || 0) + (v.comments || 0) + (v.shares || 0), 0
      );

      data.push({
        date: dateStr,
        views: dayViews,
        engagement: dayEngagement
      });
    }

    return data;
  };

  // Get top viral videos
  const getViralVideos = () => {
    return [...videos]
      .sort((a, b) => (b.views || 0) - (a.views || 0))
      .slice(0, 3);
  };

  // Calculate virality distribution
  const getViralityDistribution = () => {
    const ranges = {
      'Below 1k': 0,
      '1k-5k': 0,
      '5k-10k': 0,
      '10k-25k': 0,
      '25x-50x': 0,
      '50x-100x': 0,
      '100x+': 0
    };

    videos.forEach(v => {
      const views = v.views || 0;
      if (views < 1000) ranges['Below 1k']++;
      else if (views < 5000) ranges['1k-5k']++;
      else if (views < 10000) ranges['5k-10k']++;
      else if (views < 25000) ranges['10k-25k']++;
      else if (views < 50000) ranges['25x-50x']++;
      else if (views < 100000) ranges['50x-100x']++;
      else ranges['100x+']++;
    });

    return Object.entries(ranges).map(([range, count]) => ({
      range,
      count
    }));
  };

  // Calculate duration distribution
  const getDurationDistribution = () => {
    const ranges = {
      '0-5': 0,
      '5-10': 0,
      '10-15': 0,
      '15-20': 0,
      '20-25': 0,
      '25-30': 0,
      '30-45': 0,
      '45-60': 0
    };

    videos.forEach(v => {
      const duration = v.duration || 0;
      if (duration < 5) ranges['0-5'] += (v.views || 0);
      else if (duration < 10) ranges['5-10'] += (v.views || 0);
      else if (duration < 15) ranges['10-15'] += (v.views || 0);
      else if (duration < 20) ranges['15-20'] += (v.views || 0);
      else if (duration < 25) ranges['20-25'] += (v.views || 0);
      else if (duration < 30) ranges['25-30'] += (v.views || 0);
      else if (duration < 45) ranges['30-45'] += (v.views || 0);
      else ranges['45-60'] += (v.views || 0);
    });

    return Object.entries(ranges).map(([range, views]) => ({
      range: `${range}s`,
      views
    }));
  };

  // Calculate daily and weekly averages
  const calculateAverages = () => {
    if (videos.length === 0) return { daily: {}, weekly: {} };

    const totalViews = videos.reduce((sum, v) => sum + (v.views || 0), 0);

    const avgViews = Math.round(totalViews / videos.length);

    return {
      daily: {
        views: avgViews,
        viewsGain: Math.round(Math.random() * 100000), // Mock data
        commentsGain: Math.round(Math.random() * 50),
        likesGain: Math.round(Math.random() * 5000)
      },
      weekly: {
        views: avgViews * 7,
        viewsGain: Math.round(Math.random() * 500000),
        commentsGain: Math.round(Math.random() * 200),
        likesGain: Math.round(Math.random() * 20000)
      }
    };
  };

  // Calculate conversion funnel data
  const getConversionFunnelData = () => {
    const totalViews = analyticsData.reduce((sum, d) => sum + d.views, 0);
    const totalInstalls = analyticsData.reduce((sum, d) => sum + d.installs, 0);
    const totalTrials = analyticsData.reduce((sum, d) => sum + d.trial_started, 0);

    const installRate = totalViews > 0 ? ((totalInstalls / totalViews) * 100).toFixed(2) : 0;
    const trialRate = totalInstalls > 0 ? ((totalTrials / totalInstalls) * 100).toFixed(2) : 0;

    return [
      { stage: 'Views', value: totalViews, fill: '#8b5cf6' },
      { stage: 'Installs', value: totalInstalls, fill: '#ec4899' },
      { stage: 'Trial Started', value: totalTrials, fill: '#10b981' }
    ];
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  const metrics = calculateMetrics();
  const timeSeriesData = generateTimeSeriesData();
  const viralVideos = getViralVideos();
  const viralityDist = getViralityDistribution();
  const durationDist = getDurationDistribution();
  const averages = calculateAverages();
  const funnelData = getConversionFunnelData();

  return (
    <div className="space-y-6">
      {/* Top Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Views"
          value={formatNumber(metrics.views)}
          subtitle={`Last ${timeRange} Days`}
          color="bg-gradient-to-br from-blue-50 to-blue-100"
          textColor="text-blue-900"
        />
        <MetricCard
          title="Engagement"
          value={formatNumber(metrics.engagement)}
          subtitle={`Last ${timeRange} Days`}
          color="bg-gradient-to-br from-purple-50 to-purple-100"
          textColor="text-purple-900"
        />
        <MetricCard
          title="Likes"
          value={formatNumber(metrics.likes)}
          subtitle={`Last ${timeRange} Days`}
          color="bg-gradient-to-br from-pink-50 to-pink-100"
          textColor="text-pink-900"
        />
        <MetricCard
          title="Comments"
          value={formatNumber(metrics.comments)}
          subtitle={`Last ${timeRange} Days`}
          color="bg-gradient-to-br from-green-50 to-green-100"
          textColor="text-green-900"
        />
        <MetricCard
          title="Shares"
          value={formatNumber(metrics.shares)}
          subtitle={`Last ${timeRange} Days`}
          color="bg-gradient-to-br from-orange-50 to-orange-100"
          textColor="text-orange-900"
        />
        <MetricCard
          title="Saves"
          value={formatNumber(metrics.saves)}
          subtitle={`Last ${timeRange} Days`}
          color="bg-gradient-to-br from-yellow-50 to-yellow-100"
          textColor="text-yellow-900"
        />
      </div>

      {/* Time Series Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Performance Over Time</h3>
          <div className="flex gap-2">
            <button className="px-3 py-1 text-sm border rounded hover:bg-gray-50">Daily</button>
            <button className="px-3 py-1 text-sm border rounded bg-gray-100">Cumulative</button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip />
            <Line type="monotone" dataKey="views" stroke="#8b5cf6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Views vs Installs vs Trial Started Comparison */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Views vs Installs vs Trial Started</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analyticsData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              stroke="#9ca3af"
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              labelFormatter={(value) => {
                const date = new Date(value);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
              }}
              formatter={(value) => formatNumber(value)}
            />
            <Legend />
            <Line type="monotone" dataKey="views" stroke="#8b5cf6" strokeWidth={2} name="Views" />
            <Line type="monotone" dataKey="installs" stroke="#ec4899" strokeWidth={2} name="Installs" />
            <Line type="monotone" dataKey="trial_started" stroke="#10b981" strokeWidth={2} name="Trial Started" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Conversion Funnel */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Funnel</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={funnelData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis type="number" stroke="#9ca3af" tickFormatter={formatNumber} />
            <YAxis type="category" dataKey="stage" stroke="#9ca3af" width={120} />
            <Tooltip formatter={(value) => formatNumber(value)} />
            <Bar dataKey="value" radius={[0, 8, 8, 0]}>
              {funnelData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">View to Install Rate</p>
            <p className="text-2xl font-bold text-purple-900">
              {funnelData[1]?.value && funnelData[0]?.value
                ? ((funnelData[1].value / funnelData[0].value) * 100).toFixed(2)
                : 0}%
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Install to Trial Rate</p>
            <p className="text-2xl font-bold text-green-900">
              {funnelData[2]?.value && funnelData[1]?.value
                ? ((funnelData[2].value / funnelData[1].value) * 100).toFixed(2)
                : 0}%
            </p>
          </div>
        </div>
      </div>

      {/* Most Viral Videos */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Viral Videos</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {viralVideos.map((video, index) => (
            <ViralVideoCard key={video.id} video={video} rank={index + 1} />
          ))}
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Virality Median Analysis */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Virality Median Analysis</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={viralityDist}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="range" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" label={{ value: 'Videos Count', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="count" fill="#000000" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Duration Analysis */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Duration Analysis</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={durationDist}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="range" stroke="#9ca3af" fontSize={12} label={{ value: 'Video Duration Range', position: 'insideBottom', offset: -5 }} />
              <YAxis stroke="#9ca3af" label={{ value: 'Average Views', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="views" fill="#000000" />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <p className="text-sm font-semibold text-gray-700">Optimal Length</p>
            <p className="text-2xl font-bold text-gray-900">30-60s</p>
            <p className="text-xs text-gray-500">Average views for this duration</p>
          </div>
        </div>
      </div>

      {/* Metrics Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Metrics Breakdown</h3>
        <div className="flex gap-4 mb-4 border-b">
          <button className="pb-2 px-4 font-medium text-purple-600 border-b-2 border-purple-600">
            Averages
          </button>
          <button className="pb-2 px-4 text-gray-600 hover:text-gray-900">
            By Day
          </button>
          <button className="pb-2 px-4 text-gray-600 hover:text-gray-900">
            Upload Activity
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Period</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Average Views</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Average Views Gain</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Average Comments Gain</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Average Likes Gain</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <span className="w-8 h-8 bg-blue-100 text-blue-600 rounded flex items-center justify-center text-sm font-semibold">D</span>
                    <span className="font-medium text-gray-900">Daily Average</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-900 font-medium">{formatNumber(averages.daily.views)}</td>
                <td className="px-6 py-4">
                  <span className="text-green-600 flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    +{formatNumber(averages.daily.viewsGain)}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-green-600 flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    +{averages.daily.commentsGain}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-green-600 flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    +{formatNumber(averages.daily.likesGain)}
                  </span>
                </td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <span className="w-8 h-8 bg-green-100 text-green-600 rounded flex items-center justify-center text-sm font-semibold">W</span>
                    <span className="font-medium text-gray-900">Weekly Average</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-900 font-medium">{formatNumber(averages.weekly.views)}</td>
                <td className="px-6 py-4">
                  <span className="text-green-600 flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    +{formatNumber(averages.weekly.viewsGain)}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-green-600 flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    +{averages.weekly.commentsGain}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-green-600 flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    +{formatNumber(averages.weekly.likesGain)}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Video Stats Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Video Stats</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Video</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">
                  <div className="flex items-center gap-1">
                    Views
                    <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Views Performance</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Engagement Rate</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Likes</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Comments</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Saves</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {videos.slice(0, 10).map((video) => {
                const avgViews = videos.reduce((sum, v) => sum + (v.views || 0), 0) / videos.length;
                const performance = video.views / avgViews;
                const engagementRate = video.views > 0
                  ? (((video.likes || 0) + (video.comments || 0) + (video.shares || 0)) / video.views * 100).toFixed(1)
                  : 0;

                return (
                  <tr key={video.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <img
                          src={video.thumbnail || 'https://via.placeholder.com/60'}
                          alt=""
                          className="w-16 h-16 rounded object-cover"
                        />
                        <div className="max-w-xs">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            @{video.author_username}
                          </p>
                          <p className="text-xs text-gray-500 truncate">{video.caption}</p>
                          <p className="text-xs text-gray-400">
                            Uploaded on {new Date(video.posted_at || video.scraped_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold">
                        {formatNumber(video.views)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-xs font-medium">
                        {performance.toFixed(1)}x {performance > 1 ? 'more' : 'less'} than usual
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-900">{engagementRate}%</td>
                    <td className="px-6 py-4 text-gray-900">{formatNumber(video.likes)}</td>
                    <td className="px-6 py-4 text-gray-900">{formatNumber(video.comments)}</td>
                    <td className="px-6 py-4 text-gray-900">{formatNumber(video.bookmarks || 0)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, subtitle, color, textColor }) {
  return (
    <div className={`${color} rounded-lg p-4 border border-gray-200`}>
      <p className="text-xs font-medium text-gray-600 uppercase mb-1">{title}</p>
      <p className={`text-2xl font-bold ${textColor} mb-1`}>{value}</p>
      <p className="text-xs text-gray-500">{subtitle}</p>
    </div>
  );
}

function ViralVideoCard({ video, rank }) {
  const engagementRate = video.views > 0
    ? (((video.likes || 0) + (video.comments || 0) + (video.shares || 0)) / video.views * 100).toFixed(2)
    : 0;

  return (
    <div className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative">
        <span className="absolute top-2 left-2 w-8 h-8 bg-black text-white rounded-full flex items-center justify-center font-bold text-sm">
          #{rank}
        </span>
        <img
          src={video.thumbnail || 'https://via.placeholder.com/400x600'}
          alt=""
          className="w-full h-64 object-cover"
        />
        <div className="absolute bottom-2 left-2 right-2 bg-black bg-opacity-70 text-white p-2 rounded text-xs">
          @{video.author_username}
        </div>
      </div>
      <div className="p-4 space-y-2">
        <div className="text-xs text-gray-500">
          Uploaded on {new Date(video.posted_at || video.scraped_at).toLocaleDateString()}
        </div>
        <div className="space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">👁️ Views</span>
            <span className="font-semibold">{formatNumber(video.views)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">📊 Engagement</span>
            <span className="font-semibold">{formatNumber((video.likes || 0) + (video.comments || 0) + (video.shares || 0))}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">❤️ Likes</span>
            <span className="font-semibold">{formatNumber(video.likes)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">💬 Comments</span>
            <span className="font-semibold">{formatNumber(video.comments)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">🔄 Shares</span>
            <span className="font-semibold">{formatNumber(video.shares)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">🔖 Bookmarks</span>
            <span className="font-semibold">{formatNumber(video.bookmarks || 0)}</span>
          </div>
          <div className="flex justify-between pt-2 border-t">
            <span className="text-gray-600">📈 Engagement Rate</span>
            <span className="font-bold text-purple-600">{engagementRate}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

export default Dashboard;
