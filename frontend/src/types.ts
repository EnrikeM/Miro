export interface User {
    id: string;
    email: string;
}

export interface AuthResponse {
    token: string;
}

export interface Dashboard {
    id: string;
    name: string;
    role: 'creator' | 'editor' | 'viewer';
}

export interface Sticker {
    id: string;
    dashboard_id: string;
    x: number;
    y: number;
    text: string;
    width: number;
    height: number;
    color: string;
}

export interface DashboardDetail extends Dashboard {
    stickers: Sticker[];
}
