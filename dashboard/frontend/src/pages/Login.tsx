import React from 'react';
import { Shield } from 'lucide-react';
import { GlassCard } from '../components/GlassCard';
import { HeroCircuitBackground } from '../components/HeroCircuitBackground';

export const Login = () => {
    const [isLoading, setIsLoading] = React.useState(false);

    const handleGoogleLogin = () => {
        setIsLoading(true);
        // Use environment variable for backend URL
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        window.location.href = `${apiUrl}/auth/login`;
    };

    return (
        <div className="min-h-screen bg-black text-white overflow-hidden relative flex items-center justify-center">
            {/* Background */}
            <div className="absolute inset-0 bg-gradient-to-b from-black via-slate-950 to-black"></div>
            <div className="absolute inset-0">
                <HeroCircuitBackground />
            </div>

            <div className="relative z-10 w-full max-w-md px-6">
                <GlassCard>
                    <div className="p-8 text-center">
                        <div className="flex flex-col items-center mb-8">
                            {/* Logo Glow */}
                            <div className="relative mb-6">
                                <div className="absolute inset-0 bg-emerald-500/30 blur-xl rounded-full"></div>
                                <Shield className="w-16 h-16 text-emerald-400 relative z-10" />
                            </div>

                            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 mb-2">
                                ShadowGuard
                            </h1>
                            <p className="text-gray-400">Secure Dashboard Access</p>
                        </div>

                        <button
                            onClick={handleGoogleLogin}
                            disabled={isLoading}
                            aria-label="Sign in with Google"
                            className={`w-full group relative overflow-hidden bg-emerald-500 hover:bg-emerald-400 text-black font-bold py-3 px-4 rounded-xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] ${isLoading ? 'opacity-75 cursor-not-allowed' : ''
                                }`}
                        >
                            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>

                            <div className="relative flex items-center justify-center">
                                {isLoading ? (
                                    <span className="flex items-center">
                                        <div className="w-5 h-5 border-t-2 border-black rounded-full animate-spin mr-3"></div>
                                        Redirecting...
                                    </span>
                                ) : (
                                    <>
                                        <div className="bg-white p-1 rounded-full mr-3">
                                            <img
                                                src="https://www.google.com/favicon.ico"
                                                alt="Google"
                                                className="w-4 h-4"
                                            />
                                        </div>
                                        <span>Sign in with Google</span>
                                    </>
                                )}
                            </div>
                        </button>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
};
