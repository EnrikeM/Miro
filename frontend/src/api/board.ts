import type { Dashboard, DashboardDetail } from '../types';

import { apiClient } from './axios';

export const boardApi = {
    getBoards: async (): Promise<Dashboard[]> => {
        const response = await apiClient.get<Dashboard[]>('/board');
        return response.data;
    },

    createBoard: async (name: string): Promise<Dashboard> => {
        const response = await apiClient.post<Dashboard>('/board', { name });
        return response.data;
    },

    getBoard: async (id: string): Promise<DashboardDetail> => {
        const response = await apiClient.get<DashboardDetail>(`/board/${id}`);
        return response.data;
    },

    inviteUser: async (
        dashboardId: string,
        email: string,
        role: 'editor' | 'viewer',
    ): Promise<void> => {
        await apiClient.post(`/invite`, { dashboard_id: dashboardId, email, role });
    },
};
