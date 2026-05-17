import { useState } from 'react';
import { Layout, Menu, theme, Avatar, Space, Typography } from 'antd';
import {
  HomeOutlined,
  BookOutlined,
  FileTextOutlined,
  AimOutlined,
  BarChartOutlined,
  UserOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';
import { useAppSelector } from '../../store';

const { Sider } = Layout;
const { Text } = Typography;

type MenuItem = Required<MenuProps>['items'][number];

const learningMenuItems: MenuItem[] = [
  { 
    key: '/', 
    icon: <HomeOutlined />, 
    label: '首页',
  },
  {
    key: '/courses',
    icon: <BookOutlined />,
    label: '课程',
  },
  {
    key: '/mistakes',
    icon: <FileTextOutlined />,
    label: '错题本',
  },
  {
    key: '/goals',
    icon: <AimOutlined />,
    label: '目标与任务',
  },
  {
    key: '/progress',
    icon: <BarChartOutlined />,
    label: '学习进度',
  },
];

const accountMenuItems: MenuItem[] = [
  { 
    key: '/profile', 
    icon: <UserOutlined />, 
    label: '个人资料',
  },
  { 
    key: '/settings', 
    icon: <SettingOutlined />, 
    label: '设置',
  },
];

interface SidebarProps {
  collapsed?: boolean;
}

export default function Sidebar({ collapsed = false }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { profile } = useAppSelector((state) => state.user);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    navigate(e.key);
  };

  return (
    <Sider trigger={null} collapsible collapsed={collapsed}>
      <div
        style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <div
          style={{
            color: '#fff',
            fontSize: '16px',
            fontWeight: 'bold',
            margin: '16px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {!collapsed && '🎓 智能学习系统'}
          {collapsed && '📚'}
        </div>
      </div>

      <div style={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={learningMenuItems}
          onClick={handleMenuClick}
          style={{ flex: 1 }}
        />

        {!collapsed && profile && (
          <div
            style={{
              padding: '16px',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              cursor: 'pointer',
            }}
            onClick={() => navigate('/profile')}
          >
            <Space>
              <Avatar 
                size="small" 
                src={profile.avatar}
                icon={<UserOutlined />}
                style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
              />
              <div style={{ flex: 1, overflow: 'hidden' }}>
                <Text style={{ color: '#fff', display: 'block', fontSize: 12 }} ellipsis>
                  {profile.name}
                </Text>
                <Text type="secondary" style={{ fontSize: 10 }}>
                  查看资料
                </Text>
              </div>
            </Space>
          </div>
        )}

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={accountMenuItems}
          onClick={handleMenuClick}
          style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}
        />
      </div>
    </Sider>
  );
}
