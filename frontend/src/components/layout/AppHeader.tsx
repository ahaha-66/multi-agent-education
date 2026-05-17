import { Layout, Button, Typography } from 'antd';
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';

const { Header } = Layout;
const { Title } = Typography;

interface AppHeaderProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function AppHeader({ collapsed, onToggle }: AppHeaderProps) {
  return (
    <Header style={{ padding: '0 24px', background: '#fff', display: 'flex', alignItems: 'center' }}>
      <Button
        type="text"
        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        onClick={onToggle}
        style={{ fontSize: '16px', width: 64, height: 64 }}
      />
      <div style={{ marginLeft: '16px' }}>
        <Title level={4} style={{ margin: 0 }}>
          多Agent智能教育系统
        </Title>
      </div>
    </Header>
  );
}
