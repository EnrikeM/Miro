import { Navigate, Route, Routes } from 'react-router-dom';

import { ProtectedRoute } from '@/components';
import { Board, Dashboard, ResetPassword, SignIn, SignUp } from '@/pages';

export const App = () => {
    return (
        <Routes>
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/reset-password" element={<ResetPassword />} />

            <Route element={<ProtectedRoute />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/board/:id" element={<Board />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};
