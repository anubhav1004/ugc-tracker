import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Video,
  Users,
  Folder,
  Search,
  ChevronDown,
  ChevronRight,
  Plus,
  Sun,
  Moon,
  X
} from 'lucide-react';
import axios from 'axios';
import CreateCollectionModal from './CreateCollectionModal';
import { useTheme } from '../ThemeContext';
import { useFilters } from '../FilterContext';
import { useMobileNav } from '../MobileNavContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Sidebar() {
  const location = useLocation();
  const { isDark, toggleTheme } = useTheme();
  const { selectedPlatform, setSelectedPlatform, selectedCollection, setSelectedCollection } = useFilters();
  const { isSidebarOpen, closeSidebar } = useMobileNav();
  const [collectionsOpen, setCollectionsOpen] = useState(true);
  const [collections, setCollections] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/collections`);
      setCollections(response.data);
    } catch (error) {
      console.error('Error fetching collections:', error);
    }
  };

  const handleCollectionCreated = () => {
    fetchCollections(); // Refresh collections list
  };

  const isActive = (path) => location.pathname === path;

  const NavItem = ({ to, icon: Icon, label, badge }) => (
    <Link
      to={to}
      onClick={() => {
        // Close sidebar on mobile when navigating
        if (window.innerWidth < 1024) {
          closeSidebar();
        }
      }}
      className={`flex items-center px-3 py-2 text-sm rounded-lg transition-colors min-h-[44px] ${
        isActive(to)
          ? 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-300 font-medium'
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
      }`}
    >
      <Icon className="w-4 h-4 mr-3" />
      <span className="flex-1">{label}</span>
      {badge && (
        <span className="bg-pink-500 text-white text-xs rounded-full px-2 py-0.5 font-medium">
          {badge}
        </span>
      )}
    </Link>
  );

  return (
    <div className={`
      w-64
      bg-white dark:bg-gray-800
      border-r border-gray-200 dark:border-gray-700
      h-screen
      flex flex-col
      transition-all duration-300 ease-in-out
      fixed lg:static
      top-0 left-0
      z-50
      ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
    `}>
      {/* Logo/Brand */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">VA</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">Viral Analytics</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">Pro Curious</p>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {isDark ? (
                <Sun className="w-5 h-5 text-yellow-500" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>

            {/* Mobile close button */}
            <button
              onClick={closeSidebar}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Close menu"
            >
              <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Filters Section */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="space-y-2">
          <select
            value={selectedCollection}
            onChange={(e) => setSelectedCollection(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Collections</option>
            {collections.map((collection) => (
              <option key={collection.id} value={collection.id}>{collection.name}</option>
            ))}
          </select>

          <select className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option>All Accounts</option>
          </select>

          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Platforms</option>
            <option value="tiktok">TikTok</option>
            <option value="youtube">YouTube</option>
            <option value="instagram">Instagram</option>
          </select>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <NavItem to="/" icon={Home} label="Overview" />
        <NavItem to="/all-videos" icon={Video} label="All Videos" />
        <NavItem to="/all-accounts" icon={Users} label="All Accounts" />
        <NavItem to="/add-accounts" icon={Plus} label="Add Accounts" />

        {/* Collections Section */}
        <div className="pt-4">
          <button
            onClick={() => setCollectionsOpen(!collectionsOpen)}
            className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            {collectionsOpen ? (
              <ChevronDown className="w-4 h-4 mr-2" />
            ) : (
              <ChevronRight className="w-4 h-4 mr-2" />
            )}
            <Folder className="w-4 h-4 mr-2" />
            <span className="flex-1 text-left font-medium">Collections</span>
          </button>

          {collectionsOpen && (
            <div className="mt-2 ml-6 space-y-1">
              {/* Search Collections */}
              <div className="relative mb-2">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
                <input
                  type="text"
                  placeholder="Search Collections"
                  className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Collection Items */}
              {collections.length === 0 ? (
                <div className="text-sm text-gray-500 dark:text-gray-400 px-3 py-2 text-center">
                  No collections yet
                </div>
              ) : (
                collections.map((collection) => (
                  <Link
                    key={collection.id}
                    to={`/collections/${collection.id}`}
                    onClick={() => {
                      // Close sidebar on mobile when navigating
                      if (window.innerWidth < 1024) {
                        closeSidebar();
                      }
                    }}
                    className={`flex items-center px-3 py-2 text-sm rounded-lg transition-colors min-h-[44px] ${
                      location.pathname === `/collections/${collection.id}`
                        ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white font-medium'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div
                      className="w-3 h-3 rounded mr-2"
                      style={{ backgroundColor: collection.color || '#8B5CF6' }}
                    />
                    <span className="flex-1">{collection.name}</span>
                    {collection.is_default && (
                      <span className="text-xs text-gray-400 dark:text-gray-500">Default</span>
                    )}
                  </Link>
                ))
              )}

              {/* New Collection Button */}
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center w-full px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Collection
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Bottom Section */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
          <div className="flex items-center justify-between text-gray-700 dark:text-gray-300">
            <span className="font-medium">330/1,000</span>
          </div>
          <p className="text-xs">Videos tracked this month</p>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-2">
            <div className="bg-purple-600 dark:bg-purple-500 h-1.5 rounded-full" style={{width: '33%'}}></div>
          </div>
        </div>
      </div>

      {/* Create Collection Modal */}
      <CreateCollectionModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleCollectionCreated}
      />
    </div>
  );
}

export default Sidebar;
