import { useEffect, useState } from 'react';
import {
  Row,
  Col,
  Card,
  Button,
  Typography,
  Progress,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Tag,
  List,
} from 'antd';
import { PlusOutlined, CheckCircleOutlined, EditOutlined } from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import {
  fetchGoals,
  createGoal,
  completeGoal,
  fetchTasks,
} from '../store/slices/goalSlice';
import type { LearnerGoalCreate } from '../types/goal';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

export default function GoalsTasksPage() {
  const [form] = Form.useForm();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { goals, tasks, loading } = useAppSelector((state) => state.goal);

  useEffect(() => {
    dispatch(fetchGoals({ learnerId }));
    dispatch(fetchTasks({ learnerId }));
  }, [dispatch, learnerId]);

  const handleCreateGoal = () => {
    setCreateModalOpen(true);
  };

  const handleSubmitCreate = (values: any) => {
    const goalData: LearnerGoalCreate = {
      title: values.title,
      description: values.description,
      targetDate: values.targetDate?.toISOString(),
    };
    dispatch(createGoal({ learnerId, data: goalData }));
    setCreateModalOpen(false);
    form.resetFields();
  };

  const handleCompleteGoal = (goalId: string) => {
    dispatch(completeGoal({ learnerId, goalId }));
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'pending':
        return <Tag color="default">待开始</Tag>;
      case 'active':
        return <Tag color="blue">进行中</Tag>;
      case 'completed':
        return <Tag color="green">已完成</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  return (
    <Row gutter={[16, 16]}>
      <Col span={24}>
        <Card
          title="我的目标"
          extra={
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateGoal}>
              创建目标
            </Button>
          }
        >
          <List
            grid={{ gutter: 16, column: 3 }}
            dataSource={goals}
            renderItem={(goal) => (
              <List.Item>
                <Card
                  title={goal.title}
                  extra={getStatusTag(goal.status)}
                  actions={
                    goal.status !== 'completed'
                      ? [
                          <Button
                            type="link"
                            icon={<CheckCircleOutlined />}
                            onClick={() => handleCompleteGoal(goal.id)}
                            key="complete"
                          >
                            完成目标
                          </Button>,
                        ]
                      : []
                  }
                >
                  <Text type="secondary" ellipsis={{ rows: 3 }}>
                    {goal.description}
                  </Text>
                  <Progress
                    percent={Math.round(goal.progress * 100)}
                    style={{ marginTop: 16 }}
                  />
                  {goal.targetDate && (
                    <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                      截止日期: {new Date(goal.targetDate).toLocaleDateString()}
                    </Text>
                  )}
                </Card>
              </List.Item>
            )}
          />
        </Card>
      </Col>

      <Col span={24}>
        <Card title="任务看板">
          <Row gutter={16}>
            <Col span={8}>
              <Card title="待办" size="small" type="inner">
                <List
                  dataSource={tasks.filter((t) => t.status === 'pending')}
                  renderItem={(task) => <List.Item>{task.title}</List.Item>}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card title="进行中" size="small" type="inner">
                <List
                  dataSource={tasks.filter((t) => t.status === 'in_progress')}
                  renderItem={(task) => <List.Item>{task.title}</List.Item>}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card title="已完成" size="small" type="inner">
                <List
                  dataSource={tasks.filter((t) => t.status === 'completed')}
                  renderItem={(task) => <List.Item>{task.title}</List.Item>}
                />
              </Card>
            </Col>
          </Row>
        </Card>
      </Col>

      <Modal
        title="创建学习目标"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        onOk={() => form.submit()}
        okText="创建"
        cancelText="取消"
      >
        <Form form={form} onFinish={handleSubmitCreate} layout="vertical">
          <Form.Item
            name="title"
            label="目标标题"
            rules={[{ required: true, message: '请输入目标标题' }]}
          >
            <Input placeholder="例如：本周掌握第一章" />
          </Form.Item>

          <Form.Item name="description" label="目标描述">
            <TextArea rows={3} placeholder="请描述你的学习目标" />
          </Form.Item>

          <Form.Item name="targetDate" label="目标日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Row>
  );
}
