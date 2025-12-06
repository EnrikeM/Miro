import type { Sticker } from '../types';

import { apiClient } from './axios';

export const stickerApi = {
    createOrUpdate: async (
        sticker: Partial<Sticker> & { dashboard_id: string },
    ): Promise<Sticker> => {
        if (sticker.id && !sticker.id.startsWith('temp-') && !sticker.id.startsWith('creating-')) {
            // Update
            const response = await apiClient.put<Sticker>(`/stickers/${sticker.id}`, sticker);
            return response.data;
        } else {
            // Create
            const response = await apiClient.post<Sticker>('/stickers', sticker);
            return response.data;
        }
    },

    delete: async (id: string): Promise<void> => {
        await apiClient.delete(`/stickers/${id}`);
    },
};
