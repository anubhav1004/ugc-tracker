import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './ThemeContext';
import { FilterProvider } from './FilterContext';
import Sidebar from './components/Sidebar';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import AllVideos from './components/AllVideos';
import AllAccounts from './components/AllAccounts';
import AddAccounts from './components/AddAccounts';
import URLScraper from './components/URLScraper';
import HashtagSearch from './components/HashtagSearch';
import TrendingAudio from './components/TrendingAudio';

function App() {
  return (
    <ThemeProvider>
      <FilterProvider>
        <Router>
          <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors overflow-hidden">
            {/* Left Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
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
            </main>
          </div>
        </Router>
      </FilterProvider>
    </ThemeProvider>
  );
}

export default App;
