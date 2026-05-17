import { ReactNode } from 'react';
import { Layout } from 'antd';

const { Content } = Layout;

interface AppContentProps {
  children: ReactNode;
}

export default function AppContent({ children }: AppContentProps) {
  return (
    <Content
      style={{
        margin: '24px 16px',
        padding: 24,
        minHeight: 280,
        background: '#fff',
        borderRadius: '8px',
      }}
    >
      {children}
    </Content>
  );
}
