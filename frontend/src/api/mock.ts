import type { AxiosInstance } from 'axios';

import type { Dashboard, DashboardDetail, Sticker, User } from '../types';

const USERS_KEY = 'mock_users';
const BOARDS_KEY = 'mock_boards';
const STICKERS_KEY = 'mock_stickers';
const BOARD_ROLES_KEY = 'mock_board_roles';

const getStore = <T>(key: string, defaultVal: T): T => {
    const kept = localStorage.getItem(key);
    return kept ? JSON.parse(kept) : defaultVal;
};
const setStore = (key: string, val: any) => localStorage.setItem(key, JSON.stringify(val));

export const setupMocks = (axios: AxiosInstance) => {
    const delay = (ms = 500) => new Promise((r) => setTimeout(r, ms));

    axios.interceptors.request.use(async (config) => {
        await delay();

        const { method, url, data } = config;
        const authHeader = config.headers.Authorization as string;
        const token = authHeader?.replace('Bearer ', '');

        if (url === '/signup' && method === 'post') {
            const users = getStore<User[]>(USERS_KEY, []);
            if (users.find((u: any) => u.email === data.email)) {
                throw { response: { status: 400, data: { message: 'Email exists' } } };
            }
            const newUser = { id: crypto.randomUUID(), email: data.email, password: data.password };
            users.push(newUser);
            setStore(USERS_KEY, users);
            return {
                ...config,
                adapter: () =>
                    Promise.resolve({
                        data: {},
                        status: 200,
                        statusText: 'OK',
                        headers: {},
                        config,
                    }),
            };
        }

        if (url === '/signin' && method === 'post') {
            const users = getStore<any[]>(USERS_KEY, []);
            const user = users.find((u) => u.email === data.email && u.password === data.password);
            if (!user) {
                throw { response: { status: 404, data: { message: 'Invalid credentials' } } };
            }
            return {
                ...config,
                adapter: () =>
                    Promise.resolve({
                        data: { token: user.id },
                        status: 200,
                        statusText: 'OK',
                        headers: {},
                        config,
                    }),
            };
        }

        const currentUserId = token;
        if (!currentUserId && !url?.startsWith('/signin') && !url?.startsWith('/signup')) {
            throw { response: { status: 401, data: { message: 'Unauthorized' } } };
        }

        if (url === '/board' && method === 'get') {
            const roles = getStore<any[]>(BOARD_ROLES_KEY, []);
            const boards = getStore<Dashboard[]>(BOARDS_KEY, []);

            const userRoles = roles.filter((r) => r.user_id === currentUserId);
            const userBoards = userRoles
                .map((r) => {
                    const b = boards.find((b) => b.id === r.dashboard_id);
                    return b ? { ...b, role: r.role } : null;
                })
                .filter(Boolean);

            return {
                ...config,
                adapter: () =>
                    Promise.resolve({
                        data: userBoards,
                        status: 200,
                        statusText: 'OK',
                        headers: {},
                        config,
                    }),
            };
        }

        if (url === '/board' && method === 'post') {
            const boards = getStore<Dashboard[]>(BOARDS_KEY, []);
            const roles = getStore<any[]>(BOARD_ROLES_KEY, []);

            const newBoard = { id: crypto.randomUUID(), name: data.name };
            boards.push(newBoard as any);
            roles.push({ dashboard_id: newBoard.id, user_id: currentUserId, role: 'creator' });

            setStore(BOARDS_KEY, boards);
            setStore(BOARD_ROLES_KEY, roles);

            return {
                ...config,
                adapter: () =>
                    Promise.resolve({
                        data: newBoard,
                        status: 200,
                        statusText: 'OK',
                        headers: {},
                        config,
                    }),
            };
        }

        const boardMatch = url?.match(/^\/board\/(.+)$/);
        if (boardMatch && method === 'get') {
            const boardId = boardMatch[1];
            const boards = getStore<Dashboard[]>(BOARDS_KEY, []);
            const allStickers = getStore<Sticker[]>(STICKERS_KEY, []);
            const roles = getStore<any[]>(BOARD_ROLES_KEY, []);

            const board = boards.find((b) => b.id === boardId);

            if (!board) throw { response: { status: 404 } };

            let roleFn = roles.find(
                (r) => r.dashboard_id === boardId && r.user_id === currentUserId,
            );

            // Auto-grant viewer access if no role exists
            if (!roleFn) {
                roleFn = { dashboard_id: boardId, user_id: currentUserId, role: 'viewer' };
                roles.push(roleFn);
                setStore(BOARD_ROLES_KEY, roles);
            }

            const boardStickers = allStickers.filter((s) => s.dashboard_id === boardId);
            const result: DashboardDetail = {
                ...board,
                role: roleFn.role,
                stickers: boardStickers,
            };

            return {
                ...config,
                adapter: () =>
                    Promise.resolve({
                        data: result,
                        status: 200,
                        statusText: 'OK',
                        headers: {},
                        config,
                    }),
            };
        }

        const stickerMatch = url?.match(/^\/sticker\/(.+)$/);
        if (stickerMatch) {
            const idParam = stickerMatch[1];

            if (method === 'post') {
                const allStickers = getStore<Sticker[]>(STICKERS_KEY, []);
                let savedSticker: Sticker;
                const existingIdx = allStickers.findIndex((s) => s.id === idParam);

                if (idParam === 'new' || existingIdx === -1) {
                    savedSticker = { ...data, id: data.id || crypto.randomUUID() };
                    allStickers.push(savedSticker);
                } else {
                    allStickers[existingIdx] = { ...allStickers[existingIdx], ...data };
                    savedSticker = allStickers[existingIdx];
                }
                setStore(STICKERS_KEY, allStickers);
                return {
                    ...config,
                    adapter: () =>
                        Promise.resolve({
                            data: savedSticker,
                            status: 200,
                            statusText: 'OK',
                            headers: {},
                            config,
                        }),
                };
            }

            if (method === 'delete') {
                const allStickers = getStore<Sticker[]>(STICKERS_KEY, []);
                const newStickers = allStickers.filter((s) => s.id !== idParam);
                setStore(STICKERS_KEY, newStickers);
                return {
                    ...config,
                    adapter: () =>
                        Promise.resolve({
                            data: {},
                            status: 200,
                            statusText: 'OK',
                            headers: {},
                            config,
                        }),
                };
            }
        }

        const inviteMatch = url?.match(/^\/invite$/);
        if (inviteMatch && method === 'post') {
            const { dashboard_id, email, role } = data;

            const boards = getStore<Dashboard[]>(BOARDS_KEY, []);
            if (!boards.find((b) => b.id === dashboard_id))
                throw { response: { status: 404, data: { message: 'Board not found' } } };

            const users = getStore<User[]>(USERS_KEY, []);
            const targetUser = users.find((u) => u.email === email);

            if (!targetUser) {
                throw {
                    response: { status: 404, data: { message: 'User with this email not found' } },
                };
            }

            const targetUserId = targetUser.id;

            const roles = getStore<any[]>(BOARD_ROLES_KEY, []);

            const existingIdx = roles.findIndex(
                (r) => r.dashboard_id === dashboard_id && r.user_id === targetUserId,
            );
            if (existingIdx >= 0) {
                roles[existingIdx].role = role;
            } else {
                roles.push({ dashboard_id, user_id: targetUserId, role });
            }
            setStore(BOARD_ROLES_KEY, roles);

            return {
                ...config,
                adapter: () =>
                    Promise.resolve({
                        data: {},
                        status: 200,
                        statusText: 'OK',
                        headers: {},
                        config,
                    }),
            };
        }

        return config;
    });
};
