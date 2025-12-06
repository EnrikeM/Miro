import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { authApi } from '@/api/auth';
import { ThemeToggle } from '@/components';
import { useTheme } from '@/store';

export const SignUp: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Пароли не совпадают');
            return;
        }

        setLoading(true);
        try {
            await authApi.signup(email, password);
            navigate('/signin');
        } catch (err) {
            console.error(err);
            setError('Регистрация не удалась. Пользователь с таким email уже существует');
        } finally {
            setLoading(false);
        }
    };

    const { theme } = useTheme();

    return (
        <div
            className={`min-h-screen flex items-center justify-center font-sans overflow-hidden relative transition-colors duration-300 ${theme === 'dark' ? 'bg-gray-950 text-white' : 'bg-gray-100 text-gray-900'}`}
        >
            <div className="absolute top-4 right-4 z-50">
                <ThemeToggle />
            </div>
            <div
                className={`absolute inset-0 pointer-events-none ${theme === 'dark' ? 'bg-gradient-to-tl from-purple-900/20 via-black to-blue-900/20' : 'bg-gradient-to-tl from-purple-100 via-white to-blue-100'}`}
            />
            <div className="absolute w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-3xl -top-32 -right-32 animate-pulse" />

            <div
                className={`relative z-10 w-full max-w-sm p-8 backdrop-blur-xl border rounded-2xl shadow-2xl animate-fade-in-up ${theme === 'dark' ? 'bg-white/5 border-white/10' : 'bg-white/80 border-white/50'}`}
            >
                <h2 className="text-3xl font-bold text-center mb-2 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                    CU:Create
                </h2>
                <p
                    className={`text-center mb-8 text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}
                >
                    Зарегистрируйтесь, чтобы продолжить
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

                    <div>
                        <label
                            className={`block text-xs font-medium uppercase tracking-wider mb-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}
                        >
                            Подтвердите пароль
                        </label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all text-sm ${theme === 'dark' ? 'bg-black/20 border-white/10 placeholder-gray-600' : 'bg-gray-50 border-gray-200 placeholder-gray-400'}`}
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-purple-500/25 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                    >
                        {loading ? 'Создание аккаунта...' : 'Зарегистрироваться'}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-500">
                    Уже есть аккаунт?{' '}
                    <Link
                        to="/signin"
                        className={`transition-colors font-medium ${theme === 'dark' ? 'text-white hover:text-purple-400' : 'text-purple-600 hover:text-purple-800'}`}
                    >
                        Войти
                    </Link>
                </p>
            </div>
        </div>
    );
};
