import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'es-MX' | 'en';

interface LanguageContextValue {
  lang: Language;
  setLang: (lang: Language) => void;
  toggleLanguage: () => void;
  t: (es: string, en: string) => string;
}

const LanguageContext = createContext<LanguageContextValue>({
  lang: 'es-MX',
  setLang: () => {},
  toggleLanguage: () => {},
  t: (es) => es,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Language>(() => {
    try {
      const saved = localStorage.getItem('sacl_ui_lang');
      if (saved === 'en' || saved === 'es-MX') return saved;
    } catch {
      // ignore storage errors
    }
    return 'es-MX';
  });

  const setLang = (next: Language) => {
    setLangState(next);
    try {
      localStorage.setItem('sacl_ui_lang', next);
    } catch {
      // ignore
    }
  };

  const toggleLanguage = () => {
    setLang(lang === 'es-MX' ? 'en' : 'es-MX');
  };

  useEffect(() => {
    document.documentElement.lang = lang === 'es-MX' ? 'es-MX' : 'en';
  }, [lang]);

  const t = (es: string, en: string) => (lang === 'es-MX' ? es : en);

  return (
    <LanguageContext.Provider value={{ lang, setLang, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
