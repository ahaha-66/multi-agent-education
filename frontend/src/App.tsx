import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Layout, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { Provider } from 'react-redux';
import { store } from './store';
import Sidebar from './components/layout/Sidebar';
import AppHeader from './components/layout/AppHeader';
import AppContent from './components/layout/AppContent';
import HomePage from './pages/Home';
import CourseListPage from './pages/CourseList';
import CourseDetailPage from './pages/CourseDetail';
import PracticePage from './pages/Practice';
import KnowledgeGraphPage from './pages/KnowledgeGraph';
import MistakeBookPage from './pages/MistakeBook';
import GoalsTasksPage from './pages/GoalsTasks';
import ProgressDashboardPage from './pages/ProgressDashboard';

const { Content } = Layout;

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  return (
    <Provider store={store}>
      <ConfigProvider locale={zhCN}>
        <Router>
          <Layout style={{ minHeight: '100vh' }}>
            <Sidebar collapsed={collapsed} />
            <Layout>
              <AppHeader
                collapsed={collapsed}
                onToggle={() => setCollapsed(!collapsed)}
              />
              <AppContent>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/courses" element={<CourseListPage />} />
                  <Route path="/courses/:courseId" element={<CourseDetailPage />} />
                  <Route path="/courses/:courseId/practice" element={<PracticePage />} />
                  <Route path="/courses/:courseId/knowledge-graph" element={<KnowledgeGraphPage />} />
                  <Route path="/mistakes" element={<MistakeBookPage />} />
                  <Route path="/goals" element={<GoalsTasksPage />} />
                  <Route path="/progress" element={<ProgressDashboardPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </AppContent>
            </Layout>
          </Layout>
        </Router>
      </ConfigProvider>
    </Provider>
  );
}
