import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { boardApi } from '@/api/board';
import { stickerApi } from '@/api/sticker';
import { Sticker } from '@/components';
import { useTheme } from '@/store';
import type { DashboardDetail, Sticker as StickerType } from '@/types';

type Tool = 'cursor' | 'sticker';
const COLORS = [
    '#fff9b1', // Yellow
    '#daf7a6', // Green
    '#ffc3a0', // Orange
    '#ffafb0', // Red
    '#e0ffff', // Cyan
    '#dcd0ff', // Purple
    '#d3d3d3', // Gray
    '#ffffff', // White
];

export const Board: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [board, setBoard] = useState<DashboardDetail | null>(null);
    const [stickers, setStickers] = useState<StickerType[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [activeTool, setActiveTool] = useState<Tool>('cursor');
    const [selectedColor, setSelectedColor] = useState(COLORS[0]);

    const [interaction, setInteraction] = useState<{
        type: 'none' | 'drag' | 'resize' | 'create';
        id: string | null;
        handle?: string;
        start: { x: number; y: number };
        initial: { x: number; y: number; w: number; h: number };
    }>({ type: 'none', id: null, start: { x: 0, y: 0 }, initial: { x: 0, y: 0, w: 0, h: 0 } });

    const isEditor = board?.role === 'editor';
    const isViewer = board?.role === 'viewer';

    const loadBoard = useCallback(
        async (boardId: string) => {
            try {
                const data = await boardApi.getBoard(boardId);
                setBoard(data);
                setStickers(data.stickers || []);
            } catch (err) {
                console.error(err);
                navigate('/', { state: { error: 'Нет доступа к доске' } });
            }
        },
        [navigate],
    );

    const createSticker = async (sticker: Partial<StickerType>) => {
        if (!id || isViewer) return;
        const newStickerData = {
            dashboard_id: id,
            text: '',
            width: 200,
            height: 200,
            color: selectedColor,
            ...sticker,
        };

        try {
            const tempId = 'temp-' + Date.now();
            const tempSticker = { ...newStickerData, id: tempId } as StickerType;
            setStickers((prev) => [...prev, tempSticker]);

            const created = await stickerApi.createOrUpdate(newStickerData);
            setStickers((prev) => prev.map((s) => (s.id === tempId ? created : s)));
            return created.id;
        } catch (err) {
            console.error('Failed to create sticker', err);
        }
    };

    const updateSticker = async (stickerId: string, updates: Partial<StickerType>) => {
        if (isViewer) return;
        setStickers((prev) => prev.map((s) => (s.id === stickerId ? { ...s, ...updates } : s)));
        try {
            const current = stickers.find((s) => s.id === stickerId);
            if (!current && !updates.dashboard_id) return;
            await stickerApi.createOrUpdate({
                ...current,
                ...updates,
                id: stickerId,
                dashboard_id: id!,
            });
        } catch (err) {
            console.error('Failed to update sticker', err);
        }
    };

    const handleDelete = useCallback(
        async (stickerId: string) => {
            if (isViewer) return;
            setStickers((prev) => prev.filter((s) => s.id !== stickerId));
            if (selectedId === stickerId) setSelectedId(null);
            try {
                await stickerApi.delete(stickerId);
            } catch (err) {
                console.error(err);
            }
        },
        [isViewer, selectedId],
    );

    const handleCanvasMouseDown = (e: React.MouseEvent) => {
        if (activeTool === 'sticker' && !isViewer) {
            const canvasRect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            const startX = e.clientX - canvasRect.left;
            const startY = e.clientY - canvasRect.top;

            const tempId = 'creating-' + Date.now();
            const newSticker = {
                id: tempId,
                dashboard_id: id!,
                x: startX,
                y: startY,
                width: 0,
                height: 0,
                text: '',
                color: selectedColor,
            };
            setStickers((prev) => [...prev, newSticker]);
            setInteraction({
                type: 'create',
                id: tempId,
                start: { x: e.clientX, y: e.clientY },
                initial: { x: startX, y: startY, w: 0, h: 0 },
            });
        } else {
            setSelectedId(null);
        }
    };

    const handleStickerMouseDown = (e: React.MouseEvent, id: string) => {
        if (activeTool === 'sticker') return;
        const sticker = stickers.find((s) => s.id === id);
        if (!sticker) return;

        if (isViewer) return;

        setInteraction({
            type: 'drag',
            id,
            start: { x: e.clientX, y: e.clientY },
            initial: { x: sticker.x, y: sticker.y, w: sticker.width, h: sticker.height },
        });
    };

    const handleResizeStart = (e: React.MouseEvent, id: string, handle: string) => {
        if (isViewer) return;
        const sticker = stickers.find((s) => s.id === id);
        if (!sticker) return;
        setInteraction({
            type: 'resize',
            id,
            handle,
            start: { x: e.clientX, y: e.clientY },
            initial: { x: sticker.x, y: sticker.y, w: sticker.width, h: sticker.height },
        });
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        const { type, id: moveId, start, initial, handle } = interaction;
        if (type === 'none' || !moveId) return;

        const deltaX = e.clientX - start.x;
        const deltaY = e.clientY - start.y;

        if (type === 'drag') {
            setStickers((prev) =>
                prev.map((s) =>
                    s.id === moveId ? { ...s, x: initial.x + deltaX, y: initial.y + deltaY } : s,
                ),
            );
        } else if (type === 'create') {
            const w = Math.abs(deltaX);
            const h = Math.abs(deltaY);
            const x = deltaX < 0 ? initial.x + deltaX : initial.x;
            const y = deltaY < 0 ? initial.y + deltaY : initial.y;

            setStickers((prev) =>
                prev.map((s) =>
                    s.id === moveId
                        ? { ...s, x, y, width: Math.max(10, w), height: Math.max(10, h) }
                        : s,
                ),
            );
        } else if (type === 'resize' && handle) {
            let nX = initial.x;
            let nY = initial.y;
            let nW = initial.w;
            let nH = initial.h;

            if (handle.includes('r')) nW = initial.w + deltaX;
            if (handle.includes('l')) {
                nX = initial.x + deltaX;
                nW = initial.w - deltaX;
            }
            if (handle.includes('b')) nH = initial.h + deltaY;
            if (handle.includes('t')) {
                nY = initial.y + deltaY;
                nH = initial.h - deltaY;
            }

            if (nW < 50) nW = 50;
            if (nH < 50) nH = 50;

            setStickers((prev) =>
                prev.map((s) =>
                    s.id === moveId ? { ...s, x: nX, y: nY, width: nW, height: nH } : s,
                ),
            );
        }
    };

    const handleMouseUp = async () => {
        const { type, id: moveId } = interaction;
        if (type === 'none' || !moveId) return;

        const sticker = stickers.find((s) => s.id === moveId);
        if (sticker && !isViewer) {
            if (type === 'create') {
                const finalSticker = {
                    ...sticker,
                    width: Math.max(sticker.width, 100),
                    height: Math.max(sticker.height, 100),
                };
                setStickers((prev) => prev.filter((s) => s.id !== moveId));
                const newId = await createSticker({ ...finalSticker, id: undefined });
                if (newId) setSelectedId(newId);
                setActiveTool('cursor');
            } else {
                updateSticker(moveId, {
                    x: sticker.x,
                    y: sticker.y,
                    width: sticker.width,
                    height: sticker.height,
                });
            }
        }
        setInteraction({
            type: 'none',
            id: null,
            start: { x: 0, y: 0 },
            initial: { x: 0, y: 0, w: 0, h: 0 },
        });
    };

    const handleColorChange = (color: string) => {
        if (isViewer) return;
        setSelectedColor(color);
        if (selectedId) {
            updateSticker(selectedId, { color });
        }
    };

    const handleShare = () => {
        navigator.clipboard.writeText(window.location.href);
        alert('Ссылка на доску скопирована в буфер обмена');
    };

    const [showInvite, setShowInvite] = useState(false);
    const [inviteEmail, setInviteEmail] = useState('');
    const [inviteRole, setInviteRole] = useState<'editor' | 'viewer'>('editor');

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await boardApi.inviteUser(id!, inviteEmail, inviteRole);
            alert('Пользователь приглашен');
            setShowInvite(false);
            setInviteEmail('');
        } catch (err) {
            console.error(err);
            alert(
                'Не удалось пригласить пользователя. Пользователь должен иметь аккаунт с этим email.',
            );
        }
    };

    const { theme, toggleTheme } = useTheme();

    useEffect(() => {
        if (id) loadBoard(id);
    }, [id, loadBoard]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId && !isViewer) {
                if (
                    document.activeElement?.tagName === 'TEXTAREA' ||
                    document.activeElement?.tagName === 'INPUT'
                )
                    return;
                handleDelete(selectedId);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [selectedId, stickers, isViewer, handleDelete]);

    return (
        <div
            id="canvas"
            className={`w-full h-screen overflow-hidden relative ${activeTool === 'cursor' ? 'cursor-default' : 'cursor-crosshair'} transition-colors duration-300 ${theme === 'dark' ? 'bg-[#1a1a2e]' : 'bg-gray-100'} board-grid`}
            style={{
                backgroundImage:
                    theme === 'dark'
                        ? 'radial-gradient(#6b7280 0.5px, transparent 1px)'
                        : 'radial-gradient(#9ca3af 0.5px, transparent 1px)',
                backgroundSize: '35px 35px',
            }}
            onMouseDown={handleCanvasMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
        >
            <div
                className={`absolute top-0 left-0 right-0 h-16 backdrop-blur-md shadow-sm flex items-center px-4 z-50 justify-between border-b pointer-events-none transition-colors duration-300 ${theme === 'dark' ? 'bg-black/60 border-white/10 text-white' : 'bg-white/80 border-gray-200 text-gray-800'}`}
            >
                <div className="flex items-center gap-4 pointer-events-auto">
                    <Link
                        to="/"
                        className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent"
                    >
                        CU:Create
                    </Link>
                    <span className={`${theme === 'dark' ? 'text-gray-600' : 'text-gray-300'}`}>
                        /
                    </span>
                    <h1
                        className={`text-lg font-medium max-w-32 truncate ${theme === 'dark' ? 'text-gray-200' : 'text-gray-700'}`}
                    >
                        {board?.name || 'Загрузка...'}
                    </h1>
                    {isViewer ||
                        (isEditor && (
                            <span
                                className={`text-xs px-2 py-1 rounded-full uppercase font-bold tracking-wider ${theme === 'dark' ? 'bg-white/20 text-gray-300' : 'bg-gray-200 text-gray-600'}`}
                            >
                                {isViewer ? 'режим чтения' : 'режим редактирования'}
                            </span>
                        ))}
                </div>

                {board && !isViewer && (
                    <div
                        className={`absolute left-1/2 -translate-x-1/2 flex items-center gap-2 rounded-lg shadow-lg border p-1 pointer-events-auto transition-colors duration-300 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}
                        onMouseDown={(e) => e.stopPropagation()}
                    >
                        <button
                            onClick={() => setActiveTool('cursor')}
                            className={`p-2 rounded-md transition-all ${activeTool === 'cursor' ? 'bg-purple-500/20 text-purple-400' : theme === 'dark' ? 'hover:bg-white/10 text-gray-400' : 'hover:bg-gray-100 text-gray-500'}`}
                            title="Cursor (V)"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            >
                                <path d="m3 3 7.07 16.97 2.51-7.39 7.39-2.51L3 3z" />
                                <path d="m13 13 6 6" />
                            </svg>
                        </button>
                        <button
                            onClick={() => setActiveTool('sticker')}
                            className={`p-2 rounded-md transition-all ${activeTool === 'sticker' ? 'bg-purple-500/20 text-purple-400' : theme === 'dark' ? 'hover:bg-white/10 text-gray-400' : 'hover:bg-gray-100 text-gray-500'}`}
                            title="Sticker (S)"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            >
                                <path d="M15.5 3H5a2 2 0 0 0-2 2v14c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2V8.5L15.5 3Z" />
                                <path d="M15 3v6h6" />
                            </svg>
                        </button>

                        <div
                            className={`w-px h-6 mx-1 ${theme === 'dark' ? 'bg-white/20' : 'bg-gray-200'}`}
                        />

                        <div className="flex gap-1 pr-1">
                            {COLORS.map((c) => (
                                <button
                                    key={c}
                                    onClick={() => handleColorChange(c)}
                                    className={`w-5 h-5 rounded-full border border-black/10 transition-transform ${selectedColor === c ? 'scale-125 ring-2 ring-purple-400 ring-offset-1' : 'hover:scale-110'}`}
                                    style={{ backgroundColor: c }}
                                />
                            ))}
                        </div>
                    </div>
                )}

                <div className="flex gap-2 pointer-events-auto">
                    <button
                        onClick={toggleTheme}
                        className={`p-2 rounded-lg transition-colors ${theme === 'dark' ? 'bg-white/10 text-yellow-300 hover:bg-white/20' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                        title="Toggle Theme"
                    >
                        {theme === 'dark' ? (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            >
                                <circle cx="12" cy="12" r="5" />
                                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
                            </svg>
                        ) : (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            >
                                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                            </svg>
                        )}
                    </button>

                    {board && !isViewer && !isEditor && (
                        <>
                            <button
                                onClick={() => setShowInvite(true)}
                                className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors shadow-lg shadow-purple-500/20"
                            >
                                Пригласить
                            </button>
                            <button
                                onClick={handleShare}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${theme === 'dark' ? 'bg-white/10 text-gray-200 hover:bg-white/20' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                            >
                                Поделиться ссылкой
                            </button>
                        </>
                    )}
                </div>
            </div>

            {stickers.map((sticker) => (
                <Sticker
                    key={sticker.id}
                    data={sticker}
                    isSelected={selectedId === sticker.id}
                    onSelect={(id) => {
                        setSelectedId(id);
                        if (!isViewer) setSelectedColor(sticker.color);
                    }}
                    onUpdate={(id, updates) => updateSticker(id, updates)}
                    onDelete={handleDelete}
                    onMouseDown={handleStickerMouseDown}
                    onResizeStart={handleResizeStart}
                    readOnly={isViewer}
                />
            ))}

            {showInvite && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
                    <div
                        className={`rounded-xl shadow-2xl p-6 w-full max-w-sm animate-fade-in-up border ${theme === 'dark' ? 'bg-gray-800 border-white/10 text-white' : 'bg-white border-transparent text-gray-800'}`}
                        onMouseDown={(e) => e.stopPropagation()}
                    >
                        <h2 className="text-xl font-bold mb-4">Пригласить</h2>
                        <form onSubmit={handleInvite}>
                            <div className="mb-4">
                                <label
                                    className={`block text-xs font-bold uppercase mb-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}
                                >
                                    Email
                                </label>
                                <input
                                    type="email"
                                    value={inviteEmail}
                                    onChange={(e) => setInviteEmail(e.target.value)}
                                    className={`w-full border rounded p-2 focus:border-purple-500 outline-none ${theme === 'dark' ? 'bg-black/30 border-white/10 text-white' : 'bg-white border-gray-300 text-gray-800'}`}
                                    placeholder="user@example.com"
                                    required
                                />
                            </div>
                            <div className="mb-6">
                                <label
                                    className={`block text-xs font-bold uppercase mb-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}
                                >
                                    Роль
                                </label>
                                <select
                                    value={inviteRole}
                                    onChange={(e) =>
                                        setInviteRole(e.target.value as 'editor' | 'viewer')
                                    }
                                    className={`w-full border rounded p-2 focus:border-purple-500 outline-none ${theme === 'dark' ? 'bg-black/30 border-white/10 text-white' : 'bg-white border-gray-300 text-gray-800'}`}
                                >
                                    <option value="editor">Редактирование</option>
                                    <option value="viewer">Просмотр</option>
                                </select>
                            </div>
                            <div className="flex justify-end gap-2">
                                <button
                                    type="button"
                                    onClick={() => setShowInvite(false)}
                                    className={`px-4 py-2 hover:opacity-80 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}
                                >
                                    Отменить
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                                >
                                    Отправить приглашение
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
