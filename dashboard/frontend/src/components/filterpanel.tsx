import { useState } from 'react';
import { Filter, X, Calendar, Shield, Tag, ChevronDown } from 'lucide-react';

interface FilterPanelProps {
    filters: {
        riskLevel: string[];
        timeRange: string;
        category: string[];
    };
    onFilterChange: (category: string, value: string | string[]) => void;
    onClearFilters: () => void;
}

interface FilterOption {
    value: string;
    label: string;
    color?: string;
}

interface ExpandedSections {
    riskLevel: boolean;
    timeRange: boolean;
    category: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange, onClearFilters }) => {
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [expandedSections, setExpandedSections] = useState<ExpandedSections>({
        riskLevel: true,
        timeRange: true,
        category: true
    });

    const filterOptions = {
        riskLevel: [
            { value: 'high', label: 'High Risk (>75)', color: 'text-red-400' },
            { value: 'medium', label: 'Medium Risk (40-75)', color: 'text-orange-400' },
            { value: 'low', label: 'Low Risk (<40)', color: 'text-green-400' }
        ] as FilterOption[],
        timeRange: [
            { value: 'hour', label: 'Last Hour' },
            { value: 'day', label: 'Last 24 Hours' },
            { value: 'week', label: 'Last 7 Days' },
            { value: 'month', label: 'Last 30 Days' },
            { value: 'all', label: 'All Time' }
        ] as FilterOption[],
        category: [
            { value: 'normal', label: 'Normal Events' },
            { value: 'shadow-it', label: 'Shadow IT' },
            { value: 'blacklist', label: 'Blacklisted Services' }
        ] as FilterOption[]
    };

    const toggleFilter = (category: string, value: string) => {
        if (category === 'timeRange') {
            onFilterChange(category, value);
        } else {
            const currentValues = filters[category as keyof typeof filters] as string[];
            const newValues = currentValues.includes(value)
                ? currentValues.filter((item: string) => item !== value)
                : [...currentValues, value];
            onFilterChange(category, newValues);
        }
    };

    const toggleSection = (section: keyof ExpandedSections) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const getActiveFilterCount = (): number => {
        return (
            (filters.riskLevel?.length || 0) +
            (filters.category?.length || 0) +
            (filters.timeRange !== 'all' ? 1 : 0)
        );
    };

    const activeCount = getActiveFilterCount();

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`group relative overflow-hidden px-4 py-2.5 rounded-lg border text-sm font-medium flex items-center gap-2 transition-all duration-300 ease-out transform-gpu ${
                    activeCount > 0
                        ? 'bg-blue-500/10 border-blue-500/30 text-blue-400 glow'
                        : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-600 hover:scale-105'
                }`}
            >
                {/* Hover shine effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-out"></div>
                
                <Filter className="w-4 h-4 relative z-10" />
                <span className="relative z-10">Filter</span>
                {activeCount > 0 && (
                    <div className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full font-bold min-w-[20px] flex items-center justify-center relative z-10 animate-pulse">
                        {activeCount}
                    </div>
                )}
                <ChevronDown className={`w-4 h-4 transition-transform duration-300 relative z-10 ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
                <div className="absolute top-12 right-0 w-96 rounded-xl shadow-2xl z-50 overflow-hidden animate-fade-in bg-slate-900/95 backdrop-blur-2xl border border-slate-600/20 shadow-black/50">
                    {/* Header */}
                    <div className="p-4 border-b border-slate-700/30 bg-slate-800/20">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Filter className="w-5 h-5 text-brand-400" />
                                <h3 className="font-semibold text-white">Filter Options</h3>
                            </div>
                            <div className="flex items-center gap-3">
                                {activeCount > 0 && (
                                    <button
                                        onClick={onClearFilters}
                                        className="text-xs text-slate-400 hover:text-white transition-all duration-200 px-2 py-1 rounded bg-slate-700/50 hover:bg-slate-700 hover:scale-105"
                                    >
                                        Clear all
                                    </button>
                                )}
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="text-slate-400 hover:text-white transition-all duration-200 p-1 rounded hover:bg-slate-700/50 hover:rotate-90"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Scrollable Content */}
                    <div className="max-h-96 overflow-y-auto p-4 space-y-4">
                        {/* Risk Level Filter */}
                        <div className="bg-slate-800/20 rounded-lg p-3 border border-slate-700/30 backdrop-blur-sm">
                            <button
                                onClick={() => toggleSection('riskLevel')}
                                className="w-full flex items-center justify-between mb-3 hover:bg-slate-700/30 p-2 rounded-lg transition-all duration-200 hover:scale-[1.02]"
                            >
                                <div className="flex items-center gap-2">
                                    <Shield className="w-4 h-4 text-red-400" />
                                    <span className="text-sm font-medium text-slate-200">Risk Level</span>
                                </div>
                                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${expandedSections.riskLevel ? 'rotate-180' : ''}`} />
                            </button>
                            <div className={`overflow-hidden transition-all duration-300 ease-out ${
                                expandedSections.riskLevel 
                                    ? 'max-h-96 opacity-100' 
                                    : 'max-h-0 opacity-0'
                            }`}>
                                <div className="space-y-2 pl-6">
                                    {filterOptions.riskLevel.map((option) => (
                                        <label key={option.value} className="flex items-center gap-3 cursor-pointer hover:bg-slate-700/20 p-2 rounded-lg transition-all duration-200 hover:scale-[1.02] group">
                                            <div className="relative">
                                                <input
                                                    type="checkbox"
                                                    checked={filters.riskLevel?.includes(option.value) || false}
                                                    onChange={() => toggleFilter('riskLevel', option.value)}
                                                    className="sr-only"
                                                />
                                                <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all duration-200 ${
                                                    filters.riskLevel?.includes(option.value)
                                                        ? 'bg-brand-500 border-brand-500 text-white scale-110'
                                                        : 'border-slate-500 bg-slate-800/50 group-hover:border-slate-400'
                                                }`}>
                                                    {filters.riskLevel?.includes(option.value) && (
                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                        </svg>
                                                    )}
                                                </div>
                                            </div>
                                            <span className={`text-sm font-medium transition-colors ${option.color || 'text-slate-300'}`}>{option.label}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Time Range Filter */}
                        <div className="bg-slate-800/20 rounded-lg p-3 border border-slate-700/30 backdrop-blur-sm">
                            <button
                                onClick={() => toggleSection('timeRange')}
                                className="w-full flex items-center justify-between mb-3 hover:bg-slate-700/30 p-2 rounded-lg transition-all duration-200 hover:scale-[1.02]"
                            >
                                <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-blue-400" />
                                    <span className="text-sm font-medium text-slate-200">Time Range</span>
                                </div>
                                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${expandedSections.timeRange ? 'rotate-180' : ''}`} />
                            </button>
                            <div className={`overflow-hidden transition-all duration-300 ease-out ${
                                expandedSections.timeRange 
                                    ? 'max-h-96 opacity-100' 
                                    : 'max-h-0 opacity-0'
                            }`}>
                                <div className="space-y-2 pl-6">
                                    {filterOptions.timeRange.map((option) => (
                                        <label key={option.value} className="flex items-center gap-3 cursor-pointer hover:bg-slate-700/20 p-2 rounded-lg transition-all duration-200 hover:scale-[1.02] group">
                                            <div className="relative">
                                                <input
                                                    type="radio"
                                                    name="timeRange"
                                                    checked={filters.timeRange === option.value}
                                                    onChange={() => toggleFilter('timeRange', option.value)}
                                                    className="sr-only"
                                                />
                                                <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                                                    filters.timeRange === option.value
                                                        ? 'bg-brand-500 border-brand-500 scale-110'
                                                        : 'border-slate-500 bg-slate-800/50 group-hover:border-slate-400'
                                                }`}>
                                                    {filters.timeRange === option.value && (
                                                        <div className="w-2 h-2 rounded-full bg-white"></div>
                                                    )}
                                                </div>
                                            </div>
                                            <span className="text-sm text-slate-300 font-medium">{option.label}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Category Filter */}
                        <div className="bg-slate-800/20 rounded-lg p-3 border border-slate-700/30 backdrop-blur-sm">
                            <button
                                onClick={() => toggleSection('category')}
                                className="w-full flex items-center justify-between mb-3 hover:bg-slate-700/30 p-2 rounded-lg transition-all duration-200 hover:scale-[1.02]"
                            >
                                <div className="flex items-center gap-2">
                                    <Tag className="w-4 h-4 text-purple-400" />
                                    <span className="text-sm font-medium text-slate-200">Event Category</span>
                                </div>
                                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${expandedSections.category ? 'rotate-180' : ''}`} />
                            </button>
                            <div className={`overflow-hidden transition-all duration-300 ease-out ${
                                expandedSections.category 
                                    ? 'max-h-96 opacity-100' 
                                    : 'max-h-0 opacity-0'
                            }`}>
                                <div className="space-y-2 pl-6">
                                    {filterOptions.category.map((option) => (
                                        <label key={option.value} className="flex items-center gap-3 cursor-pointer hover:bg-slate-700/20 p-2 rounded-lg transition-all duration-200 hover:scale-[1.02] group">
                                            <div className="relative">
                                                <input
                                                    type="checkbox"
                                                    checked={filters.category?.includes(option.value) || false}
                                                    onChange={() => toggleFilter('category', option.value)}
                                                    className="sr-only"
                                                />
                                                <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all duration-200 ${
                                                    filters.category?.includes(option.value)
                                                        ? 'bg-brand-500 border-brand-500 text-white scale-110'
                                                        : 'border-slate-500 bg-slate-800/50 group-hover:border-slate-400'
                                                }`}>
                                                    {filters.category?.includes(option.value) && (
                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                        </svg>
                                                    )}
                                                </div>
                                            </div>
                                            <span className="text-sm text-slate-300 font-medium">{option.label}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="p-4 border-t border-slate-700/30 bg-slate-800/20 flex justify-between items-center">
                        <span className="text-xs text-slate-400">
                            {activeCount} filter{activeCount !== 1 ? 's' : ''} active
                        </span>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium rounded-lg transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-brand-500/20"
                        >
                            Apply Filters
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FilterPanel;