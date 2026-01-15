import React, { createContext, useContext, useState } from 'react';

const FilterContext = createContext();

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within FilterProvider');
  }
  return context;
};

export const FilterProvider = ({ children }) => {
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [selectedCollection, setSelectedCollection] = useState('all');
  const [selectedAccount, setSelectedAccount] = useState('all');

  return (
    <FilterContext.Provider
      value={{
        selectedPlatform,
        setSelectedPlatform,
        selectedCollection,
        setSelectedCollection,
        selectedAccount,
        setSelectedAccount,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
};
