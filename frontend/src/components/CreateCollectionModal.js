import React, { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function CreateCollectionModal({ isOpen, onClose, onSuccess }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [color, setColor] = useState('#8B5CF6'); // Purple default
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [allAccounts, setAllAccounts] = useState([]);
  const [selectedAccountIds, setSelectedAccountIds] = useState(new Set());
  const [loadingAccounts, setLoadingAccounts] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchAccounts();
    }
  }, [isOpen]);

  const fetchAccounts = async () => {
    setLoadingAccounts(true);
    try {
      const response = await axios.get(`${API_URL}/api/accounts?limit=100`);
      setAllAccounts(response.data);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    } finally {
      setLoadingAccounts(false);
    }
  };

  const toggleAccount = (accountId) => {
    const newSelected = new Set(selectedAccountIds);
    if (newSelected.has(accountId)) {
      newSelected.delete(accountId);
    } else {
      newSelected.add(accountId);
    }
    setSelectedAccountIds(newSelected);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Create collection
      const response = await axios.post(`${API_URL}/api/collections`, {
        name,
        description,
        color
      });

      if (response.status === 200 || response.status === 201) {
        const collectionId = response.data.id;

        // Add selected accounts to collection
        for (const accountId of selectedAccountIds) {
          try {
            await axios.post(`${API_URL}/api/collections/${collectionId}/accounts/${accountId}`);
          } catch (err) {
            console.error(`Error adding account ${accountId} to collection:`, err);
          }
        }

        // Reset form
        setName('');
        setDescription('');
        setColor('#8B5CF6');
        setSelectedAccountIds(new Set());

        // Notify parent and close
        onSuccess();
        onClose();
      }
    } catch (err) {
      console.error('Error creating collection:', err);
      setError(err.response?.data?.detail || 'Failed to create collection');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">New Collection</h2>
          <button
            onClick={onClose}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Collection Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="e.g., Top Performers"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              rows="3"
              placeholder="Optional description for this collection"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Color
            </label>
            <div className="flex items-center space-x-3">
              <input
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="w-16 h-10 border border-gray-300 dark:border-gray-600 rounded cursor-pointer"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">{color}</span>
            </div>
          </div>

          {/* Account Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Accounts (Optional)
            </label>
            {loadingAccounts ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
              </div>
            ) : allAccounts.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">No accounts available</p>
            ) : (
              <div className="max-h-60 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-lg p-2 space-y-1">
                {allAccounts.map((account) => {
                  const isSelected = selectedAccountIds.has(account.id);
                  return (
                    <div
                      key={account.id}
                      onClick={() => toggleAccount(account.id)}
                      className={`flex items-center p-2 rounded cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-purple-50 dark:bg-purple-900/20 border border-purple-500'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700 border border-transparent'
                      }`}
                    >
                      {/* Checkbox */}
                      <div
                        className={`w-4 h-4 rounded flex items-center justify-center mr-2 flex-shrink-0 ${
                          isSelected
                            ? 'bg-purple-600'
                            : 'border-2 border-gray-300 dark:border-gray-600'
                        }`}
                      >
                        {isSelected && <Check className="w-3 h-3 text-white" />}
                      </div>

                      {/* Account Info */}
                      <img
                        src={account.avatar || 'https://via.placeholder.com/32'}
                        alt={account.username}
                        className="w-8 h-8 rounded-full mr-2 flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          @{account.username}
                        </p>
                      </div>
                      <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded uppercase ml-2">
                        {account.platform}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
            {selectedAccountIds.size > 0 && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {selectedAccountIds.size} account{selectedAccountIds.size !== 1 ? 's' : ''} selected
              </p>
            )}
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Collection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
