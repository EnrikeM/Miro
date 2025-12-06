import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { boardApi } from '@/api/board';
import { ThemeToggle } from '@/components';
import { useAuth, useTheme } from '@/store';
import type { Dashboard as DashboardType } from '@/types';

const boardRoles = {
    creator: 'Владелец',
    viewer: 'Просмотр',
    editor: 'Редактирование',
};

export const Dashboard: React.FC = () => {
    const { logout } = useAuth();
    const { theme } = useTheme();
    const [boards, setBoards] = useState<DashboardType[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCreating, setIsCreating] = useState(false);
    const [newBoardName, setNewBoardName] = useState('');
    const navigate = useNavigate();
    const location = useLocation();
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    useEffect(() => {
        if (location.state?.error) {
            setErrorMsg(location.state.error);
            const timer = setTimeout(() => {
                setErrorMsg(null);
                navigate(location.pathname, { replace: true, state: {} });
            }, 1500);
            return () => clearTimeout(timer);
        }
    }, [location.state, navigate, location.pathname]);

    useEffect(() => {
        loadBoards();
    }, []);

    const loadBoards = async () => {
        try {
            const data = await boardApi.getBoards();
            setBoards(data);
        } catch (error) {
            console.error('Failed to load boards', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateBoard = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newBoardName.trim()) return;

        try {
            const newBoard = await boardApi.createBoard(newBoardName);
            setBoards([...boards, newBoard]);
            setNewBoardName('');
            setIsCreating(false);
            navigate(`/board/${newBoard.id}`);
        } catch (error) {
            console.error('Failed to create board', error);
        }
    };

    return (
        <div
            className={`min-h-screen font-sans p-8 transition-colors duration-300 ${theme === 'dark' ? 'bg-gray-950 text-white' : 'bg-gray-100 text-gray-900'}`}
        >
            <div className="max-w-7xl mx-auto">
                <header className="flex justify-between items-center mb-12 relative">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        CU:Create
                    </h1>
                    <div className="flex items-center gap-4">
                        <ThemeToggle />
                        <button
                            onClick={logout}
                            className={`px-4 py-2 rounded-lg transition-colors text-sm border ${theme === 'dark' ? 'bg-white/5 hover:bg-white/10 border-white/10' : 'bg-gray-200 hover:bg-gray-300 border-gray-300 text-gray-700'}`}
                        >
                            Выйти
                        </button>
                    </div>
                    {errorMsg && (
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 bg-red-500/90 text-white px-6 py-3 rounded-full shadow-lg backdrop-blur">
                            {errorMsg}
                        </div>
                    )}
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    <div
                        onClick={() => setIsCreating(true)}
                        className={`aspect-video border rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all group hover:shadow-[0_0_20px_rgba(168,85,247,0.2)] ${theme === 'dark' ? 'bg-gradient-to-br from-purple-900/40 to-blue-900/40 border-purple-500/30 hover:border-purple-400' : 'bg-white border-purple-200 hover:border-purple-300 shadow-sm'}`}
                    >
                        <div
                            className={`w-12 h-12 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform ${theme === 'dark' ? 'bg-purple-500/20' : 'bg-purple-100'}`}
                        >
                            <span className="text-2xl text-purple-400">+</span>
                        </div>
                        <span
                            className={`font-medium ${theme === 'dark' ? 'text-purple-200' : 'text-purple-600'}`}
                        >
                            Создать новую доску
                        </span>
                    </div>

                    {loading ? (
                        <div className="col-span-3 text-gray-500">Загрузка...</div>
                    ) : (
                        boards.map((board) => (
                            <Link
                                key={board.id}
                                to={`/board/${board.id}`}
                                className={`aspect-video border rounded-xl p-6 flex flex-col justify-between transition-all hover:-translate-y-1 hover:shadow-xl ${theme === 'dark' ? 'bg-white/5 border-white/10 hover:bg-white/10' : 'bg-white border-gray-200 hover:border-purple-300 shadow-sm'}`}
                            >
                                <div>
                                    <h3
                                        className={`text-xl font-semibold mb-2 truncate ${theme === 'dark' ? 'text-white' : 'text-gray-800'}`}
                                    >
                                        {board.name}
                                    </h3>
                                    <span
                                        className={`text-xs px-2 py-1 rounded capitalize ${theme === 'dark' ? 'bg-white/10 text-gray-400' : 'bg-gray-100 text-gray-600'}`}
                                    >
                                        {boardRoles[board.role]}
                                    </span>
                                </div>
                                <div className="text-xs text-gray-500 mt-4">Открыть →</div>
                            </Link>
                        ))
                    )}
                </div>
            </div>

            {isCreating && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div
                        className={`border rounded-2xl p-8 w-full max-w-md animate-fade-in-up shadow-2xl ${theme === 'dark' ? 'bg-gray-900 border-white/10' : 'bg-white border-gray-200'}`}
                    >
                        <h2
                            className={`text-2xl font-bold mb-6 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}
                        >
                            Создать новую доску
                        </h2>
                        <form onSubmit={handleCreateBoard}>
                            <input
                                type="text"
                                autoFocus
                                value={newBoardName}
                                onChange={(e) => setNewBoardName(e.target.value)}
                                placeholder="Название"
                                className={`w-full px-4 py-3 border rounded-lg mb-6 focus:outline-none focus:border-purple-500 transition-colors ${theme === 'dark' ? 'bg-black/40 border-white/10 text-white' : 'bg-gray-50 border-gray-300 text-gray-900'}`}
                            />
                            <div className="flex justify-end gap-3">
                                <button
                                    type="button"
                                    onClick={() => setIsCreating(false)}
                                    className={`px-4 py-2 rounded-lg transition-colors ${theme === 'dark' ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-800'}`}
                                >
                                    Отмена
                                </button>
                                <button
                                    type="submit"
                                    className="px-6 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 font-semibold text-white hover:shadow-lg hover:shadow-purple-500/20 transition-all"
                                >
                                    Создать
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
