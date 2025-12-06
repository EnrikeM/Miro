import type { Sticker } from '../types';

import { apiClient } from './axios';

export const stickerApi = {
    createOrUpdate: async (
        sticker: Partial<Sticker> & { dashboard_id: string },
    ): Promise<Sticker> => {
        const id = sticker.id || 'new';
        const response = await apiClient.post<Sticker>(`/sticker/${id}`, sticker);
        return response.data;
    },

    delete: async (id: string): Promise<void> => {
        await apiClient.delete(`/sticker/${id}`);
    },
};
