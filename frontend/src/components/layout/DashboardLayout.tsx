import { FC, ReactNode } from 'react';
import { Header } from './Header';

interface DashboardLayoutProps {
    children: ReactNode;
    sidebar?: ReactNode;
}

export const DashboardLayout: FC<DashboardLayoutProps> = ({ children, sidebar }) => {
    return (
        <div className="container">
            <Header />

            <main>
                {sidebar ? (
                    <div className="dashboard-grid">
                        <div className="main-content">
                            {children}
                        </div>
                        <aside className="sidebar">
                            {sidebar}
                        </aside>
                    </div>
                ) : (
                    <div className="main-content">
                        {children}
                    </div>
                )}
            </main>
        </div>
    );
};
