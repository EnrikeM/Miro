import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { authApi } from '@/api/auth';
import { ThemeToggle } from '@/components';
import { useAuth, useTheme } from '@/store';

export const SignIn: React.FC = () => {
    const { theme } = useTheme();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const { token } = await authApi.signin(email, password);
            login(token);
            navigate('/');
        } catch (err) {
            console.error(err);
            setError('Неверный email или пароль');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            className={`min-h-screen flex items-center justify-center font-sans overflow-hidden relative transition-colors duration-300 ${theme === 'dark' ? 'bg-gray-950 text-white' : 'bg-gray-100 text-gray-900'}`}
        >
            <div className="absolute top-4 right-4 z-50">
                <ThemeToggle />
            </div>
            <div
                className={`absolute inset-0 pointer-events-none ${theme === 'dark' ? 'bg-gradient-to-br from-purple-900/20 via-black to-blue-900/20' : 'bg-gradient-to-br from-purple-100 via-white to-blue-100'}`}
            />
            <div className="absolute w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-3xl -top-20 -left-20 animate-pulse" />
            <div className="absolute w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-3xl -bottom-20 -right-20 animate-pulse delay-700" />

            <div
                className={`relative z-10 w-full max-w-sm p-8 backdrop-blur-xl border rounded-2xl shadow-2xl animate-fade-in-up ${theme === 'dark' ? 'bg-white/5 border-white/10' : 'bg-white/80 border-white/50'}`}
            >
                <h2 className="text-3xl font-bold text-center mb-2 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                    CU:Create
                </h2>
                <p
                    className={`text-center mb-8 text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}
                >
                    Войдите, чтобы продолжить
                </p>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label
                            className={`block text-xs font-medium uppercase tracking-wider mb-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}
                        >
                            Email
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all text-sm ${theme === 'dark' ? 'bg-black/20 border-white/10 placeholder-gray-600' : 'bg-gray-50 border-gray-200 placeholder-gray-400'}`}
                            placeholder="you@example.com"
                            required
                        />
                    </div>

                    <div>
                        <label
                            className={`block text-xs font-medium uppercase tracking-wider mb-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}
                        >
                            Пароль
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all text-sm ${theme === 'dark' ? 'bg-black/20 border-white/10 placeholder-gray-600' : 'bg-gray-50 border-gray-200 placeholder-gray-400'}`}
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    <div className="flex justify-end">
                        <Link
                            to="/reset-password"
                            className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
                        >
                            Забыли пароль?
                        </Link>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-purple-500/25 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Вход...' : 'Войти'}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-500">
                    Нет аккаунта?{' '}
                    <Link
                        to="/signup"
                        className={`${theme === 'dark' ? 'text-white hover:text-purple-400' : 'text-purple-600 hover:text-purple-800'} transition-colors font-medium`}
                    >
                        Зарегистрироваться
                    </Link>
                </p>
            </div>
        </div>
    );
};
