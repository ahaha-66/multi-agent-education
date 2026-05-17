import { useEffect, useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Avatar, 
  Button, 
  Form, 
  Input, 
  Select, 
  Upload, 
  Tag, 
  Space, 
  Typography,
  Divider,
  message,
  Spin,
  DatePicker,
} from 'antd';
import { 
  UserOutlined, 
  MailOutlined, 
  TrophyOutlined,
  FireOutlined,
  CalendarOutlined,
  EditOutlined,
  SaveOutlined,
  BankOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchUserProfile, updateUserProfile } from '../store/slices/userSlice';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;

export default function ProfilePage() {
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { profile, loading, error } = useAppSelector((state) => state.user);
  const [form] = Form.useForm();
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    dispatch(fetchUserProfile(learnerId));
  }, [dispatch, learnerId]);

  useEffect(() => {
    if (profile) {
      form.setFieldsValue({
        name: profile.name,
        email: profile.email,
        grade: profile.grade,
        school: profile.school,
      });
    }
  }, [profile, form]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    if (profile) {
      form.setFieldsValue({
        name: profile.name,
        email: profile.email,
        grade: profile.grade,
        school: profile.school,
      });
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const values = await form.validateFields();
      await dispatch(updateUserProfile({ userId: learnerId, data: values })).unwrap();
      message.success('个人信息更新成功！');
      setIsEditing(false);
    } catch (error) {
      message.error('更新失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  const getGradeLabel = (grade?: number) => {
    if (!grade) return '未设置';
    const labels: Record<number, string> = {
      6: '六年级',
      7: '七年级',
      8: '八年级',
      9: '九年级',
      10: '高一',
      11: '高二',
      12: '高三',
    };
    return labels[grade] || `${grade}年级`;
  };

  return (
    <Spin spinning={loading} tip="加载用户信息...">
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <UserOutlined />
                <span>个人信息</span>
              </Space>
            }
            extra={
              !isEditing ? (
                <Button 
                  type="link" 
                  icon={<EditOutlined />} 
                  onClick={handleEdit}
                >
                  编辑
                </Button>
              ) : (
                <Space>
                  <Button onClick={handleCancel}>取消</Button>
                  <Button 
                    type="primary" 
                    icon={<SaveOutlined />} 
                    onClick={handleSave}
                    loading={saving}
                  >
                    保存
                  </Button>
                </Space>
              )
            }
          >
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Upload
                showUploadList={false}
                beforeUpload={() => false}
              >
                <Avatar
                  size={120}
                  src={profile?.avatar}
                  icon={<UserOutlined />}
                  style={{ 
                    cursor: 'pointer',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  }}
                />
              </Upload>
              {!isEditing && profile && (
                <>
                  <Title level={3} style={{ marginTop: 16, marginBottom: 4 }}>
                    {profile.name}
                  </Title>
                  <Text type="secondary">学习者</Text>
                </>
              )}
            </div>

            <Form
              form={form}
              layout="vertical"
              disabled={!isEditing}
            >
              <Form.Item
                name="name"
                label="姓名"
                rules={[{ required: true, message: '请输入姓名' }]}
              >
                <Input prefix={<UserOutlined />} placeholder="请输入姓名" />
              </Form.Item>

              <Form.Item
                name="email"
                label="邮箱"
                rules={[
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
              </Form.Item>

              <Form.Item
                name="grade"
                label="年级"
              >
                <Select placeholder="请选择年级">
                  <Option value={6}>六年级</Option>
                  <Option value={7}>七年级</Option>
                  <Option value={8}>八年级</Option>
                  <Option value={9}>九年级</Option>
                  <Option value={10}>高一</Option>
                  <Option value={11}>高二</Option>
                  <Option value={12}>高三</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="school"
                label="学校"
              >
                <Input prefix={<BankOutlined />} placeholder="请输入学校名称" />
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card title="学习统计">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Card.Meta
                  title={
                    <div style={{ textAlign: 'center' }}>
                      <TrophyOutlined style={{ fontSize: 32, color: '#faad14' }} />
                      <div style={{ marginTop: 8 }}>
                        <Title level={2} style={{ margin: 0, color: '#faad14' }}>
                          {profile?.totalPoints || 0}
                        </Title>
                        <Text type="secondary">总积分</Text>
                      </div>
                    </div>
                  }
                />
              </Col>
              <Col xs={24} sm={8}>
                <Card.Meta
                  title={
                    <div style={{ textAlign: 'center' }}>
                      <FireOutlined style={{ fontSize: 32, color: '#ff4d4f' }} />
                      <div style={{ marginTop: 8 }}>
                        <Title level={2} style={{ margin: 0, color: '#ff4d4f' }}>
                          {profile?.streak || 0}
                        </Title>
                        <Text type="secondary">连续学习天数</Text>
                      </div>
                    </div>
                  }
                />
              </Col>
              <Col xs={24} sm={8}>
                <Card.Meta
                  title={
                    <div style={{ textAlign: 'center' }}>
                      <CalendarOutlined style={{ fontSize: 32, color: '#1890ff' }} />
                      <div style={{ marginTop: 8 }}>
                        <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
                          {profile?.totalStudyDays || 1}
                        </Title>
                        <Text type="secondary">学习总天数</Text>
                      </div>
                    </div>
                  }
                />
              </Col>
            </Row>
          </Card>

          <Card title="账户信息" style={{ marginTop: 16 }}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text type="secondary">用户ID：</Text>
                <Text copyable style={{ marginLeft: 8 }}>{learnerId}</Text>
              </Col>
              <Col span={12}>
                <Text type="secondary">注册时间：</Text>
                <Text>
                  {profile?.createdAt ? dayjs(profile.createdAt).format('YYYY-MM-DD') : '未知'}
                </Text>
              </Col>
              <Col span={12}>
                <Text type="secondary">最后活跃：</Text>
                <Text>
                  {profile?.lastActiveAt ? dayjs(profile.lastActiveAt).format('YYYY-MM-DD HH:mm') : '未知'}
                </Text>
              </Col>
              <Col span={12}>
                <Text type="secondary">年级：</Text>
                <Tag color="blue">{getGradeLabel(profile?.grade)}</Tag>
              </Col>
            </Row>
          </Card>

          <Card title="学习成就" style={{ marginTop: 16 }}>
            <Space wrap size="middle">
              <Tag color="gold" icon={<TrophyOutlined />} style={{ padding: '8px 16px' }}>
                初次学习
              </Tag>
              {(profile?.totalStudyDays || 0) >= 7 && (
                <Tag color="purple" icon={<FireOutlined />} style={{ padding: '8px 16px' }}>
                  一周学习
                </Tag>
              )}
              {(profile?.totalStudyDays || 0) >= 30 && (
                <Tag color="red" icon={<FireOutlined />} style={{ padding: '8px 16px' }}>
                  一个月学习
                </Tag>
              )}
              {(profile?.streak || 0) >= 7 && (
                <Tag color="orange" icon={<FireOutlined />} style={{ padding: '8px 16px' }}>
                  连续7天学习
                </Tag>
              )}
              {(profile?.totalPoints || 0) >= 100 && (
                <Tag color="green" icon={<TrophyOutlined />} style={{ padding: '8px 16px' }}>
                  积分达人
                </Tag>
              )}
            </Space>
          </Card>
        </Col>
      </Row>
    </Spin>
  );
}
