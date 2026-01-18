import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Users, Check } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const AddAccountsToCollectionModal = ({ isOpen, onClose, collection }) => {
  const [allAccounts, setAllAccounts] = useState([]);
  const [accountsInCollection, setAccountsInCollection] = useState([]);
  const [selectedAccountIds, setSelectedAccountIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen && collection) {
      fetchData();
    }
  }, [isOpen, collection]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch all accounts and accounts in this collection
      const [allAccountsRes, collectionAccountsRes] = await Promise.all([
        axios.get(`${API_URL}/api/accounts?limit=100`),
        axios.get(`${API_URL}/api/collections/${collection.id}/accounts`)
      ]);

      setAllAccounts(allAccountsRes.data);
      setAccountsInCollection(collectionAccountsRes.data);

      // Set initially selected accounts
      const initialSelected = new Set(collectionAccountsRes.data.map(acc => acc.id));
      setSelectedAccountIds(initialSelected);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    } finally {
      setLoading(false);
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

  const handleSave = async () => {
    setSaving(true);
    try {
      // Get accounts to add and remove
      const currentIds = new Set(accountsInCollection.map(acc => acc.id));
      const accountsToAdd = [...selectedAccountIds].filter(id => !currentIds.has(id));
      const accountsToRemove = [...currentIds].filter(id => !selectedAccountIds.has(id));

      // Add new accounts
      for (const accountId of accountsToAdd) {
        await axios.post(`${API_URL}/api/collections/${collection.id}/accounts/${accountId}`);
      }

      // Remove accounts
      for (const accountId of accountsToRemove) {
        await axios.delete(`${API_URL}/api/collections/${collection.id}/accounts/${accountId}`);
      }

      // Success
      onClose(true); // Pass true to indicate changes were made
    } catch (error) {
      console.error('Error saving collection accounts:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen || !collection) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Users className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Manage Accounts
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Collection: {collection.name}
              </p>
            </div>
          </div>
          <button
            onClick={() => onClose(false)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
          ) : allAccounts.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">No accounts available</p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Select accounts to include in this collection. Analytics will only show data from selected accounts.
              </p>

              {allAccounts.map((account) => {
                const isSelected = selectedAccountIds.has(account.id);

                return (
                  <div
                    key={account.id}
                    onClick={() => toggleAccount(account.id)}
                    className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      isSelected
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    {/* Checkbox */}
                    <div
                      className={`w-5 h-5 rounded flex items-center justify-center mr-3 flex-shrink-0 ${
                        isSelected
                          ? 'bg-purple-600'
                          : 'border-2 border-gray-300 dark:border-gray-600'
                      }`}
                    >
                      {isSelected && <Check className="w-4 h-4 text-white" />}
                    </div>

                    {/* Account Info */}
                    <div className="flex items-center flex-1 min-w-0">
                      <img
                        src={account.avatar || 'https://via.placeholder.com/40'}
                        alt={account.username}
                        className="w-10 h-10 rounded-full mr-3 flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="font-medium text-gray-900 dark:text-white truncate">
                            @{account.username}
                          </p>
                          <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded uppercase">
                            {account.platform}
                          </span>
                        </div>
                        {account.nickname && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                            {account.nickname}
                          </p>
                        )}
                      </div>

                      {/* Stats */}
                      <div className="ml-4 text-right flex-shrink-0">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">
                          {account.total_videos} videos
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {account.total_views?.toLocaleString()} views
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {selectedAccountIds.size} account(s) selected
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => onClose(false)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              disabled={saving}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddAccountsToCollectionModal;
