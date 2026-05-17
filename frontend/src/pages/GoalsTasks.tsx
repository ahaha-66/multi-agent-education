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
  Collapse,
  Space,
  Empty,
} from 'antd';
import {
  PlusOutlined,
  CheckCircleOutlined,
  EditOutlined,
  BookOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  RightOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import {
  fetchGoals,
  createGoal,
  completeGoal,
  fetchTasks,
  completeTask,
} from '../store/slices/goalSlice';
import { fetchCourses, fetchCourseCatalog } from '../store/slices/courseSlice';
import type { LearnerGoalCreate, LearnerGoal, LearnerTask } from '../types/goal';
import type { Course, CourseCatalog, Chapter, KnowledgePoint } from '../types/course';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { Panel } = Collapse;

export default function GoalsTasksPage() {
  const [form] = Form.useForm();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [expandedGoal, setExpandedGoal] = useState<string | null>(null);
  const [courseCatalogs, setCourseCatalogs] = useState<Record<string, CourseCatalog>>({});
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const learnerId = useAppSelector((state) => state.user.id);
  const { goals, tasks, loading } = useAppSelector((state) => state.goal);
  const { list: courses } = useAppSelector((state) => state.course);

  useEffect(() => {
    dispatch(fetchGoals({ learnerId }));
    dispatch(fetchTasks({ learnerId }));
    dispatch(fetchCourses());
  }, [dispatch, learnerId]);

  const loadCourseCatalog = async (courseId: string) => {
    if (!courseCatalogs[courseId]) {
      try {
        const catalog = await dispatch(fetchCourseCatalog(courseId)).unwrap();
        setCourseCatalogs(prev => ({ ...prev, [courseId]: catalog }));
      } catch (error) {
        console.error('Failed to fetch course catalog:', error);
      }
    }
  };

  const getGoalTasks = (goalId: string): LearnerTask[] => {
    return tasks.filter(t => t.goal_id === goalId);
  };

  const handleCreateGoal = () => {
    setCreateModalOpen(true);
  };

  const handleSubmitCreate = async (values: any) => {
    const goalData: LearnerGoalCreate = {
      title: values.title,
      description: values.description,
      course_id: values.courseId,
      targetDate: values.targetDate?.toISOString(),
    };
    await dispatch(createGoal({ learnerId, data: goalData })).unwrap();
    dispatch(fetchTasks({ learnerId }));
    setCreateModalOpen(false);
    form.resetFields();
  };

  const handleCompleteGoal = async (goalId: string) => {
    await dispatch(completeGoal({ learnerId, goalId })).unwrap();
    dispatch(fetchTasks({ learnerId }));
  };

  const handleToggleGoal = (goalId: string) => {
    setExpandedGoal(expandedGoal === goalId ? null : goalId);
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

  const getTaskTypeIcon = (type: string) => {
    switch (type) {
      case 'learn':
      case 'learning':
        return <BookOutlined />;
      case 'practice':
        return <PlayCircleOutlined />;
      case 'review':
        return <ReloadOutlined />;
      default:
        return <RightOutlined />;
    }
  };

  const getCourseName = (courseId: string | null) => {
    if (!courseId) return '通用学习';
    const course = courses.find(c => c.id === courseId);
    return course?.name || '未知课程';
  };

  const pendingGoals = goals.filter(g => g.status === 'pending');
  const activeGoals = goals.filter(g => g.status === 'active');
  const completedGoals = goals.filter(g => g.status === 'completed');

  const renderGoalCard = (goal: LearnerGoal, isCompleted: boolean) => {
    const goalTasks = getGoalTasks(goal.id);
    const isExpanded = expandedGoal === goal.id;

    const handleTaskClickWithStatus = async (task: LearnerTask) => {
      if (task.status !== 'completed' && !isCompleted) {
        await dispatch(completeTask({ learnerId, taskId: task.id })).unwrap();
        dispatch(fetchTasks({ learnerId }));
      }

      if (task.type === 'practice' && goal.course_id) {
        navigate(`/courses/${goal.course_id}/practice`);
      } else if (task.type === 'review' && goal.course_id) {
        navigate(`/courses/${goal.course_id}/practice`);
      } else if (task.knowledge_point_id && goal.course_id) {
        navigate(`/courses/${goal.course_id}`);
      } else if (goal.course_id) {
        navigate(`/courses/${goal.course_id}`);
      }
    };

    return (
      <Card
        key={goal.id}
        size="small"
        style={{ marginBottom: 12, cursor: 'pointer' }}
        onClick={() => handleToggleGoal(goal.id)}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text strong>{goal.title}</Text>
            {getStatusTag(goal.status)}
          </div>
          
          {goal.description && (
            <Text type="secondary" ellipsis={{ rows: 2 }}>
              {goal.description}
            </Text>
          )}
          
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {getCourseName(goal.course_id)}
          </Text>
          
          <Progress percent={Math.round(goal.progress * 100)} size="small" />
          
          {isExpanded && (
            <div style={{ marginTop: 12 }}>
              <Title level={5} style={{ marginBottom: 8 }}>
                {isCompleted ? '复习内容' : '学习任务'}
              </Title>
              {goalTasks.length > 0 ? (
                <List
                  dataSource={goalTasks}
                  renderItem={(task) => (
                    <List.Item
                      style={{ 
                        cursor: 'pointer', 
                        padding: '8px 0',
                        borderBottom: '1px dashed #f0f0f0'
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTaskClickWithStatus(task);
                      }}
                    >
                      <Space>
                        {getTaskTypeIcon(task.type)}
                        <div>
                          <Text strong>{task.title}</Text>
                          {task.description && (
                            <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
                              {task.description}
                            </Text>
                          )}
                        </div>
                        <Tag color={task.status === 'completed' ? 'green' : 'default'}>
                          {task.status === 'completed' ? '已完成' : '待处理'}
                        </Tag>
                      </Space>
                    </List.Item>
                  )}
                />
              ) : (
                <Empty description="暂无任务" image={Empty.PRESENTED_IMAGE_SIMPLE} />
              )}
              
              {!isCompleted && goal.status !== 'completed' && (
                <Button
                  type="primary"
                  icon={<CheckCircleOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleCompleteGoal(goal.id);
                  }}
                  style={{ marginTop: 12, width: '100%' }}
                >
                  完成目标
                </Button>
              )}
            </div>
          )}
        </Space>
      </Card>
    );
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
          <Row gutter={16}>
            <Col span={8}>
              <Card title="待办" size="small" type="inner">
                {pendingGoals.length > 0 ? (
                  pendingGoals.map(goal => renderGoalCard(goal, false))
                ) : (
                  <Empty description="暂无待办目标" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                )}
              </Card>
            </Col>
            <Col span={8}>
              <Card title="进行中" size="small" type="inner">
                {activeGoals.length > 0 ? (
                  activeGoals.map(goal => renderGoalCard(goal, false))
                ) : (
                  <Empty description="暂无进行中目标" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                )}
              </Card>
            </Col>
            <Col span={8}>
              <Card title="已完成" size="small" type="inner">
                {completedGoals.length > 0 ? (
                  completedGoals.map(goal => renderGoalCard(goal, true))
                ) : (
                  <Empty description="暂无已完成目标" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                )}
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
        width={500}
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

          <Form.Item name="courseId" label="关联课程">
            <Select placeholder="选择课程（可选）">
              {courses.map(course => (
                <Option key={course.id} value={course.id}>
                  {course.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="targetDate" label="目标日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Row>
  );
}
