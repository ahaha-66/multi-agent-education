import { useEffect, useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Switch, 
  Select, 
  Button, 
  Space, 
  Typography,
  Divider,
  message,
  Alert,
  Tabs,
} from 'antd';
import { 
  SettingOutlined, 
  BellOutlined, 
 BgColorsOutlined,
  ExperimentOutlined,
  NotificationOutlined,
  SaveOutlined,
  RedoOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import { updateUserSettings } from '../store/slices/userSlice';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

export default function SettingsPage() {
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { settings, loading } = useAppSelector((state) => state.user);
  const [localSettings, setLocalSettings] = useState(settings);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleChange = (key: string, value: any) => {
    setLocalSettings((prev: any) => {
      const keys = key.split('.');
      const newSettings = { ...prev };
      let current: any = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = value;
      
      return newSettings;
    });
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      await dispatch(updateUserSettings({ 
        userId: learnerId, 
        settings: localSettings 
      })).unwrap();
      message.success('设置已保存！');
      setHasChanges(false);
    } catch (error) {
      message.error('保存失败，请重试');
    }
  };

  const handleReset = () => {
    setLocalSettings(settings);
    setHasChanges(false);
    message.info('已恢复默认设置');
  };

  return (
    <div>
      <Title level={3}>设置</Title>
      
      {hasChanges && (
        <Alert
          message="设置已修改"
          description="您有未保存的更改，请点击保存按钮保存您的设置。"
          type="warning"
          showIcon
          action={
            <Space>
              <Button size="small" onClick={handleReset}>重置</Button>
              <Button 
                type="primary" 
                size="small" 
                icon={<SaveOutlined />}
                onClick={handleSave}
                loading={loading}
              >
                保存
              </Button>
            </Space>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      <Tabs defaultActiveKey="appearance">
        <TabPane 
          tab={
            <span>
              <BgColorsOutlined />
              外观
            </span>
          }
          key="appearance"
        >
          <Card title="主题设置">
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <div style={{ marginBottom: 16 }}>
                  <Text strong>主题模式</Text>
                  <Paragraph type="secondary">
                    选择应用的外观主题
                  </Paragraph>
                  <Select
                    value={localSettings.theme}
                    onChange={(value) => handleChange('theme', value)}
                    style={{ width: 200 }}
                  >
                    <Option value="light">
                      <Space>
                        <span>☀️</span> 浅色模式
                      </Space>
                    </Option>
                    <Option value="dark">
                      <Space>
                        <span>🌙</span> 深色模式
                      </Space>
                    </Option>
                    <Option value="auto">
                      <Space>
                        <span>⚙️</span> 跟随系统
                      </Space>
                    </Option>
                  </Select>
                </div>

                <Divider />

                <div style={{ marginBottom: 16 }}>
                  <Text strong>显示设置</Text>
                  <div style={{ marginTop: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text>显示学习进度</Text>
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            在课程卡片上显示学习进度条
                          </Paragraph>
                        </div>
                        <Switch
                          checked={localSettings.display?.showProgress}
                          onChange={(checked) => handleChange('display.showProgress', checked)}
                        />
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text>紧凑模式</Text>
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            使用更紧凑的布局，节省屏幕空间
                          </Paragraph>
                        </div>
                        <Switch
                          checked={localSettings.display?.compactMode}
                          onChange={(checked) => handleChange('display.compactMode', checked)}
                        />
                      </div>
                    </Space>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <ExperimentOutlined />
              练习设置
            </span>
          }
          key="practice"
        >
          <Card title="练习偏好">
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <div style={{ marginBottom: 16 }}>
                  <Text strong>题目难度偏好</Text>
                  <Paragraph type="secondary">
                    根据您的水平选择练习题目难度
                  </Paragraph>
                  <Select
                    value={localSettings.practice?.difficulty}
                    onChange={(value) => handleChange('practice.difficulty', value)}
                    style={{ width: 200 }}
                  >
                    <Option value="easy">
                      <Space>
                        <span>🟢</span> 简单
                      </Space>
                    </Option>
                    <Option value="medium">
                      <Space>
                        <span>🟡</span> 中等
                      </Space>
                    </Option>
                    <Option value="hard">
                      <Space>
                        <span>🔴</span> 困难
                      </Space>
                    </Option>
                  </Select>
                </div>

                <Divider />

                <div>
                  <Text strong>答题设置</Text>
                  <div style={{ marginTop: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text>自动播放提示</Text>
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            提交错误答案后自动显示提示
                          </Paragraph>
                        </div>
                        <Switch
                          checked={localSettings.practice?.autoPlayHints}
                          onChange={(checked) => handleChange('practice.autoPlayHints', checked)}
                        />
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text>立即显示答案</Text>
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                          提交答案后立即显示正确答案和解析
                          </Paragraph>
                        </div>
                        <Switch
                          checked={localSettings.practice?.showAnswerImmediately}
                          onChange={(checked) => handleChange('practice.showAnswerImmediately', checked)}
                        />
                      </div>
                    </Space>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <BellOutlined />
              通知
            </span>
          }
          key="notifications"
        >
          <Card title="通知设置">
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <div>
                  <Text strong>通知偏好</Text>
                  <Paragraph type="secondary">
                    管理您希望接收的通知类型
                  </Paragraph>
                  <div style={{ marginTop: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text>邮件通知</Text>
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            通过邮件接收重要通知和学习报告
                          </Paragraph>
                        </div>
                        <Switch
                          checked={localSettings.notifications?.email}
                          onChange={(checked) => handleChange('notifications.email', checked)}
                        />
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text>推送通知</Text>
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            通过浏览器推送通知
                          </Paragraph>
                        </div>
                        <Switch
                          checked={localSettings.notifications?.push}
                          onChange={(checked) => handleChange('notifications.push', checked)}
                        />
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Text>学习提醒</Text>
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            提醒您完成每日的学习任务
                          </Paragraph>
                        </div>
                        <Switch
                          checked={localSettings.notifications?.reminder}
                          onChange={(checked) => handleChange('notifications.reminder', checked)}
                        />
                      </div>
                    </Space>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <NotificationOutlined />
              其他
            </span>
          }
          key="other"
        >
          <Card title="其他设置">
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <div style={{ marginBottom: 16 }}>
                  <Text strong>语言设置</Text>
                  <Paragraph type="secondary">
                    选择界面显示语言
                  </Paragraph>
                  <Select
                    value={localSettings.language}
                    onChange={(value) => handleChange('language', value)}
                    style={{ width: 200 }}
                  >
                    <Option value="zh">
                      <Space>
                        <span>🇨🇳</span> 简体中文
                      </Space>
                    </Option>
                    <Option value="en">
                      <Space>
                        <span>🇺🇸</span> English
                      </Space>
                    </Option>
                  </Select>
                </div>

                <Divider />

                <div>
                  <Text strong>数据管理</Text>
                  <div style={{ marginTop: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Button 
                        icon={<RedoOutlined />}
                        onClick={() => message.info('功能开发中...')}
                      >
                        重置学习进度
                      </Button>
                      <Paragraph type="secondary">
                        此操作将清除所有学习记录和进度，请谨慎操作。
                      </Paragraph>
                    </Space>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </TabPane>
      </Tabs>

      {hasChanges && (
        <div style={{ 
          position: 'fixed', 
          bottom: 24, 
          right: 24, 
          zIndex: 1000 
        }}>
          <Space direction="vertical">
            <Button 
              shape="circle"
              size="large"
              icon={<SaveOutlined />}
              type="primary"
              onClick={handleSave}
              loading={loading}
            />
            <Button 
              shape="circle"
              size="large"
              icon={<RedoOutlined />}
              onClick={handleReset}
            />
          </Space>
        </div>
      )}
    </div>
  );
}
