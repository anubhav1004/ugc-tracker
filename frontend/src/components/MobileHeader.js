import React from 'react';
import { Menu } from 'lucide-react';
import { useMobileNav } from '../MobileNavContext';

function MobileHeader() {
  const { toggleSidebar } = useMobileNav();

  return (
    <header className="lg:hidden sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between px-4 py-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
          aria-label="Toggle menu"
        >
          <Menu className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        </button>

        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">VA</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">Viral Analytics</h1>
          </div>
        </div>

        {/* Spacer for centering */}
        <div className="w-10"></div>
      </div>
    </header>
  );
}

export default MobileHeader;
