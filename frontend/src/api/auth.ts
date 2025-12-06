import type { AuthResponse } from '../types';

import { apiClient } from './axios';

export const authApi = {
    signup: async (email: string, password: string): Promise<void> => {
        await apiClient.post('/signup', { email, password });
    },

    signin: async (email: string, password: string): Promise<AuthResponse> => {
        const response = await apiClient.post<AuthResponse>('/signin', { email, password });
        return response.data;
    },
};
