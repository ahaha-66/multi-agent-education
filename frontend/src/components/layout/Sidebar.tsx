import { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import {
  HomeOutlined,
  BookOutlined,
  BookFilled,
  FileTextOutlined,
  AimOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';

const { Sider } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

const items: MenuItem[] = [
  { key: '/',
  icon: <HomeOutlined />,
  label: '首页',
},
{
  key: '/courses',
  icon: <BookOutlined />,
  label: '课程',
},
{
  key: '/practice',
  icon: <BookFilled />,
  label: '练习',
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

interface SidebarProps {
  collapsed?: boolean;
}

export default function Sidebar({ collapsed = false }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
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
        }}
      >
        <div
          style={{
            color: '#fff',
            fontSize: '18px',
            fontWeight: 'bold',
            margin: '16px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {!collapsed && '智能学习系统'}
        </div>
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={items}
        onClick={handleMenuClick}
      />
    </Sider>
  );
}
