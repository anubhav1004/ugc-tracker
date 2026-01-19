import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './ThemeContext';
import { FilterProvider } from './FilterContext';
import { MobileNavProvider, useMobileNav } from './MobileNavContext';
import Sidebar from './components/Sidebar';
import MobileHeader from './components/MobileHeader';

// Lazy load route components for code splitting
const AnalyticsDashboard = lazy(() => import('./components/AnalyticsDashboard'));
const AllVideos = lazy(() => import('./components/AllVideos'));
const AllAccounts = lazy(() => import('./components/AllAccounts'));
const AddAccounts = lazy(() => import('./components/AddAccounts'));
const URLScraper = lazy(() => import('./components/URLScraper'));
const HashtagSearch = lazy(() => import('./components/HashtagSearch'));
const TrendingAudio = lazy(() => import('./components/TrendingAudio'));

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex items-center justify-center h-screen bg-gray-50 dark:bg-gray-900">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 dark:border-purple-400 mb-4 mx-auto"></div>
      <p className="text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
  </div>
);

// Inner component that uses mobile nav context
function AppLayout() {
  const { isSidebarOpen, closeSidebar } = useMobileNav();

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors overflow-hidden relative">
      {/* Mobile overlay backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={closeSidebar}
          aria-label="Close menu"
        />
      )}

      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto w-full lg:w-auto">
        {/* Mobile Header with Hamburger */}
        <MobileHeader />

        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<AnalyticsDashboard />} />
            <Route path="/all-videos" element={<AllVideos />} />
            <Route path="/all-accounts" element={<AllAccounts />} />
            <Route path="/add-accounts" element={<AddAccounts />} />
            <Route path="/scrape" element={<URLScraper />} />
            <Route path="/search" element={<HashtagSearch />} />
            <Route path="/trending" element={<TrendingAudio />} />
            <Route path="/collections/:name" element={<AnalyticsDashboard />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <FilterProvider>
        <MobileNavProvider>
          <Router>
            <AppLayout />
          </Router>
        </MobileNavProvider>
      </FilterProvider>
    </ThemeProvider>
  );
}

export default App;
