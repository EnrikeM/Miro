import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import { useAuth } from '@/store';

export const ProtectedRoute: React.FC = () => {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/signin" replace />;
    }

    return <Outlet />;
};
