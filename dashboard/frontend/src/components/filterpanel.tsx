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
        <>
            <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes slideDown {
                    from {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes slideUp {
                    from {
                        opacity: 1;
                        transform: translateY(0);
                    }
                    to {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                }

                @keyframes expandSection {
                    from {
                        opacity: 0;
                        max-height: 0;
                    }
                    to {
                        opacity: 1;
                        max-height: 300px;
                    }
                }

                @keyframes collapseSection {
                    from {
                        opacity: 1;
                        max-height: 300px;
                    }
                    to {
                        opacity: 0;
                        max-height: 0;
                    }
                }

                .filter-panel-enter {
                    animation: slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }

                .filter-panel-exit {
                    animation: slideUp 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }

                .section-content {
                    overflow: hidden;
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                }

                .section-expanded {
                    animation: expandSection 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }

                .section-collapsed {
                    animation: collapseSection 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }

                .glass-filter {
                    background: linear-gradient(135deg, 
                        rgba(15, 23, 42, 0.95) 0%,
                        rgba(30, 41, 59, 0.9) 50%,
                        rgba(51, 65, 85, 0.95) 100%
                    );
                    backdrop-filter: blur(24px) saturate(180%);
                    border: 1px solid rgba(148, 163, 184, 0.1);
                    box-shadow: 
                        0 25px 50px -12px rgba(0, 0, 0, 0.8),
                        0 8px 16px -8px rgba(0, 0, 0, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
                }

                .custom-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }

                .custom-scrollbar::-webkit-scrollbar-track {
                    background: rgba(30, 41, 59, 0.3);
                    border-radius: 3px;
                }

                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(148, 163, 184, 0.3);
                    border-radius: 3px;
                }

                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: rgba(148, 163, 184, 0.5);
                }

                .filter-button {
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    position: relative;
                    overflow: hidden;
                }

                .filter-button::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                    transition: left 0.5s ease;
                }

                .filter-button:hover::before {
                    left: 100%;
                }

                .checkbox-custom {
                    position: relative;
                    cursor: pointer;
                }

                .checkbox-custom input[type="checkbox"] {
                    opacity: 0;
                    position: absolute;
                }

                .checkbox-custom .checkmark {
                    width: 16px;
                    height: 16px;
                    border: 1.5px solid #475569;
                    border-radius: 4px;
                    background: rgba(30, 41, 59, 0.5);
                    position: relative;
                    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
                    flex-shrink: 0;
                }

                .checkbox-custom input[type="checkbox"]:checked + .checkmark {
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    border-color: #3b82f6;
                    transform: scale(1.1);
                }

                .checkbox-custom input[type="checkbox"]:checked + .checkmark::after {
                    content: '✓';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                }

                .radio-custom {
                    position: relative;
                    cursor: pointer;
                }

                .radio-custom input[type="radio"] {
                    opacity: 0;
                    position: absolute;
                }

                .radio-custom .radiomark {
                    width: 16px;
                    height: 16px;
                    border: 1.5px solid #475569;
                    border-radius: 50%;
                    background: rgba(30, 41, 59, 0.5);
                    position: relative;
                    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
                    flex-shrink: 0;
                }

                .radio-custom input[type="radio"]:checked + .radiomark {
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    border-color: #3b82f6;
                    transform: scale(1.1);
                }

                .radio-custom input[type="radio"]:checked + .radiomark::after {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 6px;
                    height: 6px;
                    background: white;
                    border-radius: 50%;
                }
                `
            }} />
            
            <div className="relative">
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className={`filter-button px-4 py-2.5 rounded-lg border text-sm font-medium flex items-center gap-2 ${
                        activeCount > 0
                            ? 'bg-blue-500/10 border-blue-500/30 text-blue-400 shadow-[0_0_20px_-5px_rgba(59,130,246,0.3)]'
                            : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-600'
                    }`}
                >
                    <Filter className="w-4 h-4" />
                    <span>Filter</span>
                    {activeCount > 0 && (
                        <div className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full font-bold min-w-[20px] flex items-center justify-center">
                            {activeCount}
                        </div>
                    )}
                    <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
                </button>

                {isOpen && (
                    <div className="filter-panel-enter absolute top-12 right-0 w-96 glass-filter rounded-xl shadow-2xl z-50 overflow-hidden">
                        {/* Header */}
                        <div className="p-4 border-b border-slate-700/30 bg-slate-800/20">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Filter className="w-5 h-5 text-blue-400" />
                                    <h3 className="font-semibold text-white">Filter Options</h3>
                                </div>
                                <div className="flex items-center gap-3">
                                    {activeCount > 0 && (
                                        <button
                                            onClick={onClearFilters}
                                            className="text-xs text-slate-400 hover:text-white transition-colors px-2 py-1 rounded bg-slate-700/50 hover:bg-slate-700"
                                        >
                                            Clear all
                                        </button>
                                    )}
                                    <button
                                        onClick={() => setIsOpen(false)}
                                        className="text-slate-400 hover:text-white transition-colors p-1 rounded hover:bg-slate-700/50"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Scrollable Content */}
                        <div className="max-h-96 overflow-y-auto custom-scrollbar p-4 space-y-4">
                            {/* Risk Level Filter */}
                            <div className="bg-slate-800/20 rounded-lg p-3 border border-slate-700/30">
                                <button
                                    onClick={() => toggleSection('riskLevel')}
                                    className="w-full flex items-center justify-between mb-3 hover:bg-slate-700/30 p-2 rounded-lg transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <Shield className="w-4 h-4 text-red-400" />
                                        <span className="text-sm font-medium text-slate-200">Risk Level</span>
                                    </div>
                                    <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${expandedSections.riskLevel ? 'rotate-180' : ''}`} />
                                </button>
                                <div className={`section-content ${expandedSections.riskLevel ? 'section-expanded' : 'section-collapsed'}`}>
                                    {expandedSections.riskLevel && (
                                        <div className="space-y-2 pl-6">
                                            {filterOptions.riskLevel.map((option) => (
                                                <label key={option.value} className="checkbox-custom flex items-center gap-3 cursor-pointer hover:bg-slate-700/20 p-2 rounded-lg transition-colors">
                                                    <input
                                                        type="checkbox"
                                                        checked={filters.riskLevel?.includes(option.value) || false}
                                                        onChange={() => toggleFilter('riskLevel', option.value)}
                                                    />
                                                    <div className="checkmark"></div>
                                                    <span className={`text-sm ${option.color} font-medium`}>{option.label}</span>
                                                </label>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Time Range Filter */}
                            <div className="bg-slate-800/20 rounded-lg p-3 border border-slate-700/30">
                                <button
                                    onClick={() => toggleSection('timeRange')}
                                    className="w-full flex items-center justify-between mb-3 hover:bg-slate-700/30 p-2 rounded-lg transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <Calendar className="w-4 h-4 text-blue-400" />
                                        <span className="text-sm font-medium text-slate-200">Time Range</span>
                                    </div>
                                    <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${expandedSections.timeRange ? 'rotate-180' : ''}`} />
                                </button>
                                <div className={`section-content ${expandedSections.timeRange ? 'section-expanded' : 'section-collapsed'}`}>
                                    {expandedSections.timeRange && (
                                        <div className="space-y-2 pl-6">
                                            {filterOptions.timeRange.map((option) => (
                                                <label key={option.value} className="radio-custom flex items-center gap-3 cursor-pointer hover:bg-slate-700/20 p-2 rounded-lg transition-colors">
                                                    <input
                                                        type="radio"
                                                        name="timeRange"
                                                        checked={filters.timeRange === option.value}
                                                        onChange={() => toggleFilter('timeRange', option.value)}
                                                    />
                                                    <div className="radiomark"></div>
                                                    <span className="text-sm text-slate-300 font-medium">{option.label}</span>
                                                </label>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Category Filter */}
                            <div className="bg-slate-800/20 rounded-lg p-3 border border-slate-700/30">
                                <button
                                    onClick={() => toggleSection('category')}
                                    className="w-full flex items-center justify-between mb-3 hover:bg-slate-700/30 p-2 rounded-lg transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <Tag className="w-4 h-4 text-purple-400" />
                                        <span className="text-sm font-medium text-slate-200">Event Category</span>
                                    </div>
                                    <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${expandedSections.category ? 'rotate-180' : ''}`} />
                                </button>
                                <div className={`section-content ${expandedSections.category ? 'section-expanded' : 'section-collapsed'}`}>
                                    {expandedSections.category && (
                                        <div className="space-y-2 pl-6">
                                            {filterOptions.category.map((option) => (
                                                <label key={option.value} className="checkbox-custom flex items-center gap-3 cursor-pointer hover:bg-slate-700/20 p-2 rounded-lg transition-colors">
                                                    <input
                                                        type="checkbox"
                                                        checked={filters.category?.includes(option.value) || false}
                                                        onChange={() => toggleFilter('category', option.value)}
                                                    />
                                                    <div className="checkmark"></div>
                                                    <span className="text-sm text-slate-300 font-medium">{option.label}</span>
                                                </label>
                                            ))}
                                        </div>
                                    )}
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
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors"
                            >
                                Apply Filters
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};

export default FilterPanel;