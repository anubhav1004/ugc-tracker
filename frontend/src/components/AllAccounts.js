import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Users, Video, Eye, Heart, TrendingUp, CheckCircle, Trash2 } from 'lucide-react';
import DeleteConfirmationModal from './DeleteConfirmationModal';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function AllAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [accountToDelete, setAccountToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/accounts?limit=100`);
      setAccounts(response.data);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (account) => {
    setAccountToDelete(account);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!accountToDelete) return;

    setDeleting(true);
    try {
      await axios.delete(`${API_URL}/api/accounts/${accountToDelete.id}`);

      // Remove from local state
      setAccounts(accounts.filter(acc => acc.id !== accountToDelete.id));

      // Close modal
      setDeleteModalOpen(false);
      setAccountToDelete(null);
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Failed to delete account. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteModalOpen(false);
    setAccountToDelete(null);
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
          <p className="text-gray-600 dark:text-gray-400">Loading accounts...</p>
        </div>
      </div>
    );
  }

  if (accounts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center max-w-md">
          <Users className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">No Accounts Tracked</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">Start tracking TikTok creators and get instant performance insights</p>
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">All Accounts</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{accounts.length} accounts tracked</p>
      </div>

      {/* Accounts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts.map((account) => {
          const avgViews = account.total_videos > 0 ? account.total_views / account.total_videos : 0;
          const avgLikes = account.total_videos > 0 ? account.total_likes / account.total_videos : 0;
          const engagementRate =
            account.total_views > 0
              ? (account.total_likes / account.total_views) * 100
              : 0;

          return (
            <div
              key={account.id}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
            >
              {/* Profile Header */}
              <div className="flex items-start mb-4">
                <img
                  src={account.avatar || 'https://via.placeholder.com/80'}
                  alt={account.username}
                  className="w-16 h-16 rounded-full mr-4"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center">
                    <h3 className="font-bold text-lg dark:text-white truncate">@{account.username}</h3>
                    {account.is_verified && (
                      <CheckCircle className="w-4 h-4 ml-1 text-blue-500 flex-shrink-0" />
                    )}
                  </div>
                  {account.nickname && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 truncate">{account.nickname}</p>
                  )}
                  <div className="flex items-center mt-1 space-x-2">
                    <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded uppercase font-medium">
                      {account.platform}
                    </span>
                  </div>
                </div>
              </div>

              {/* Bio */}
              {account.bio && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                  {account.bio}
                </p>
              )}

              {/* Follower Count */}
              {account.total_followers > 0 && (
                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                  <Users className="h-4 w-4" />
                  <span className="font-semibold">{formatNumber(account.total_followers)}</span>
                  <span>followers</span>
                </div>
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center text-gray-600 dark:text-gray-400 text-xs mb-1">
                    <Video className="w-3 h-3 mr-1" />
                    <span>Videos</span>
                  </div>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">{account.total_videos}</p>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center text-gray-600 dark:text-gray-400 text-xs mb-1">
                    <Eye className="w-3 h-3 mr-1" />
                    <span>Total Views</span>
                  </div>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(account.total_views)}
                  </p>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center text-gray-600 dark:text-gray-400 text-xs mb-1">
                    <Heart className="w-3 h-3 mr-1" />
                    <span>Total Likes</span>
                  </div>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(account.total_likes)}
                  </p>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center text-gray-600 dark:text-gray-400 text-xs mb-1">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    <span>Avg Views</span>
                  </div>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(Math.round(avgViews))}
                  </p>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="space-y-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Avg Likes per Video</span>
                  <span className="font-semibold dark:text-white">{formatNumber(Math.round(avgLikes))}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Engagement Rate</span>
                  <span className="font-semibold text-purple-600 dark:text-purple-400">
                    {engagementRate.toFixed(2)}%
                  </span>
                </div>
                {account.last_scraped && (
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Last Updated</span>
                    <span className="text-xs text-gray-500 dark:text-gray-500">
                      {new Date(account.last_scraped).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2 mt-4">
                <Link
                  to={`/all-videos?creator=${account.username}`}
                  className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium text-center"
                >
                  View All Videos
                </Link>
                <button
                  onClick={() => handleDeleteClick(account)}
                  className="px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                  title="Delete account"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={deleteModalOpen}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        accountName={accountToDelete?.nickname}
        accountUsername={accountToDelete?.username}
      />
    </div>
  );
}

export default AllAccounts;
