import type { Dashboard, DashboardDetail } from '../types';

import { apiClient } from './axios';

export const boardApi = {
    getBoards: async (): Promise<Dashboard[]> => {
        const response = await apiClient.get<Dashboard[]>('/boards');
        return response.data;
    },

    createBoard: async (name: string): Promise<Dashboard> => {
        const response = await apiClient.post<Dashboard[]>('/boards', { name });
        // The Python API returns the full board object, but Frontend expects Dashboard (summary)
        return response.data as unknown as Dashboard;
    },

    getBoard: async (id: string): Promise<DashboardDetail> => {
        const response = await apiClient.get<DashboardDetail>(`/boards/${id}`);
        return response.data;
    },

    inviteUser: async (
        dashboardId: string,
        email: string,
        role: 'editor' | 'viewer',
    ): Promise<void> => {
        await apiClient.post(`/boards/${dashboardId}/invite`, { email, role });
    },

    deleteBoard: async (id: string): Promise<void> => {
        await apiClient.delete(`/boards/${id}`);
    },
};
