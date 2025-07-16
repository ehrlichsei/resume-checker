import React, { createContext, useState, useMemo } from 'react';

export const languages = {
  en: 'en',
  zh: 'zh',
};

export const LangContext = createContext({
  lang: languages.en,
  toggle: () => {},
});

export const LangProvider = ({ children }) => {
  const [lang, setLang] = useState(languages.zh); // default to Chinese

  const value = useMemo(
    () => ({
      lang,
      toggle: () => setLang((prev) => (prev === languages.en ? languages.zh : languages.en)),
    }),
    [lang],
  );

  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
};
