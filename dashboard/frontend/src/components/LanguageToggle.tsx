import { motion } from 'framer-motion';
import { Globe } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

export function LanguageToggle() {
  const { language, toggleLanguage, t } = useLanguage();

  return (
    <motion.button
      onClick={toggleLanguage}
      className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-sm font-medium hover:bg-slate-700/50 hover:border-slate-600 transition-all"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      title={t.languageToggle.switchLanguage}
    >
      <Globe className="w-4 h-4 text-emerald-400" />
      <div className="flex items-center gap-1">
        <span className={`transition-colors ${language === 'en' ? 'text-emerald-400 font-semibold' : 'text-gray-400'}`}>
          {t.languageToggle.english}
        </span>
        <span className="text-gray-500">|</span>
        <span className={`transition-colors ${language === 'ja' ? 'text-emerald-400 font-semibold' : 'text-gray-400'}`}>
          {t.languageToggle.japanese}
        </span>
      </div>
    </motion.button>
  );
}
