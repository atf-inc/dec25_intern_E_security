import React from 'react';
import { Shield } from 'lucide-react';

export const Login = () => {
    const [isLoading, setIsLoading] = React.useState(false);

    const handleGoogleLogin = () => {
        setIsLoading(true);
        window.location.href = 'http://localhost:8000/auth/login';
    };

    return (
        <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
            <div className="w-full max-w-md bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700">
                <div className="flex flex-col items-center mb-8">
                    <Shield className="w-16 h-16 text-blue-500 mb-4" />
                    <h1 className="text-3xl font-bold text-white mb-2">ShadowGuard</h1>
                    <p className="text-gray-400">Secure Dashboard Access</p>
                </div>

                <button
                    onClick={handleGoogleLogin}
                    disabled={isLoading}
                    className={`w-full bg-white text-gray-900 font-bold py-3 px-4 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors ${isLoading ? 'opacity-75 cursor-not-allowed' : ''
                        }`}
                >
                    {isLoading ? (
                        <span className="flex items-center">
                            <div className="w-5 h-5 border-t-2 border-gray-900 rounded-full animate-spin mr-3"></div>
                            Redirecting...
                        </span>
                    ) : (
                        <>
                            <img
                                src="https://www.google.com/favicon.ico"
                                alt="Google"
                                className="w-6 h-6 mr-3"
                            />
                            Sign in with Google
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};
            </div >
        </div >
    );
};
