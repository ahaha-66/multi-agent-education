import { useEffect, useState, useMemo } from 'react';
import { Row, Col, Card, Button, Statistic, Progress, Spin, List, Empty, message, Space } from 'antd';
import { BookOutlined, ClockCircleOutlined, FileTextOutlined, TrophyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchOverallProgress } from '../store/slices/progressSlice';
import { fetchCourses } from '../store/slices/courseSlice';
import { mistakeApi } from '../services/mistakeApi';
import { goalTaskApi } from '../services/goalTaskApi';
import type { MistakeStatistics } from '../types/mistake';
import type { LearnerGoal, LearnerTask } from '../types/goal';
import dayjs from 'dayjs';

export default function HomePage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const user = useAppSelector((state) => state.user);
  const { overall, loading: progressLoading } = useAppSelector(
    (state) => state.progress
  );
  const { list: courses, loading: coursesLoading } = useAppSelector(
    (state) => state.course
  );
  
  const [mistakeStats, setMistakeStats] = useState<MistakeStatistics | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [recentGoals, setRecentGoals] = useState<LearnerGoal[]>([]);
  const [recentTasks, setRecentTasks] = useState<LearnerTask[]>([]);
  const [pendingReviews, setPendingReviews] = useState<LearnerTask[]>([]);

  const learningDays = useMemo(() => {
    if (user.createdAt) {
      return dayjs().diff(dayjs(user.createdAt), 'day') + 1;
    }
    return 1;
  }, [user.createdAt]);

  useEffect(() => {
    dispatch(fetchOverallProgress(learnerId));
    dispatch(fetchCourses());
    
    const fetchStats = async () => {
      setStatsLoading(true);
      try {
        const [statsResponse, goalsResponse, tasksResponse] = await Promise.all([
          mistakeApi.getStatistics(learnerId),
          goalTaskApi.getGoals(learnerId).catch(() => ({ goals: [] })),
          goalTaskApi.getTasks(learnerId).catch(() => ({ tasks: [] })),
        ]);
        
        setMistakeStats(statsResponse);
        
        if (goalsResponse?.goals) {
          setRecentGoals(goalsResponse.goals.slice(0, 3));
        }
        
        if (tasksResponse?.tasks) {
          const allTasks = tasksResponse.tasks;
          setRecentTasks(allTasks.filter(t => t.status === 'pending').slice(0, 3));
          setPendingReviews(allTasks.filter(t => t.status === 'completed' && t.type === 'review').slice(0, 5));
        }
      } catch (error) {
        console.error('Failed to fetch statistics:', error);
        message.error('加载数据失败');
      } finally {
        setStatsLoading(false);
      }
    };
    
    fetchStats();
  }, [dispatch, learnerId]);

  const handleContinueLearning = (courseId: string) => {
    navigate(`/courses/${courseId}`);
  };

  const handleReview = (task: LearnerTask) => {
    if (task.knowledge_point_id) {
      navigate(`/courses/${task.goal?.course_id || courses[0]?.id}/practice?kp=${task.knowledge_point_id}`);
    } else {
      navigate('/courses');
    }
  };

  const handleQuickTask = (task: LearnerTask) => {
    if (task.type === 'practice' || task.type === 'review') {
      const courseId = task.goal?.course_id || courses[0]?.id;
      const params = task.knowledge_point_id ? `?kp=${task.knowledge_point_id}` : '';
      navigate(`/courses/${courseId}/practice${params}`);
    } else if (task.type === 'learn' && task.knowledge_point_id) {
      const courseId = task.goal?.course_id || courses[0]?.id;
      navigate(`/courses/${courseId}?kp=${task.knowledge_point_id}`);
    } else {
      navigate('/courses');
    }
  };

  const getCourseProgress = (courseId: string) => {
    const courseProgress = overall?.courses.find((c) => c.course_id === courseId);
    return courseProgress?.overall_progress || 0;
  };

  const totalProgress = overall?.overall_progress || 0;
  const totalMistakes = mistakeStats?.total_mistakes || 0;
  const completedGoals = recentGoals.filter(g => g.status === 'completed').length;

  return (
    <Spin spinning={progressLoading || coursesLoading || statsLoading}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card 
            title={
              <Space>
                <TrophyOutlined />
                <span>学习概览</span>
              </Space>
            }
            extra={
              <Button type="link" onClick={() => navigate('/progress')}>
                查看详情
              </Button>
            }
          >
            <Row gutter={16}>
              <Col xs={24} sm={12} md={6}>
                <Card.Meta 
                  title={
                    <Statistic
                      title="总进度"
                      value={Math.round(totalProgress * 100)}
                      suffix="%"
                      valueStyle={{ 
                        color: totalProgress > 0.5 ? '#3f8600' : '#1890ff',
                        fontSize: 32
                      }}
                    />
                  }
                />
                <Progress 
                  percent={Math.round(totalProgress * 100)} 
                  status="active"
                  strokeColor={totalProgress > 0.5 ? '#52c41a' : '#1890ff'}
                  style={{ marginTop: 8 }}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="错题数量"
                  value={totalMistakes}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: totalMistakes > 0 ? '#faad14' : '#52c41a' }}
                />
                {totalMistakes > 0 && (
                  <Button 
                    type="link" 
                    size="small" 
                    onClick={() => navigate('/mistakes')}
                    style={{ marginTop: 8 }}
                  >
                    查看错题
                  </Button>
                )}
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="学习课程"
                  value={courses.length}
                  prefix={<BookOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="学习天数"
                  value={learningDays}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card 
            title={
              <Space>
                <BookOutlined />
                <span>继续学习</span>
              </Space>
            }
            extra={
              <Button type="link" onClick={() => navigate('/courses')}>
                查看全部
              </Button>
            }
          >
            {courses.length > 0 ? (
              <List
                grid={{ gutter: 16, xs: 1, sm: 1, md: 2 }}
                dataSource={courses.slice(0, 2)}
                renderItem={(course) => {
                  const progress = getCourseProgress(course.id);
                  return (
                    <List.Item>
                      <Card
                        title={
                          <Space>
                            <span>{course.name}</span>
                            <Button 
                              type="primary" 
                              size="small"
                              onClick={() => handleContinueLearning(course.id)}
                            >
                              继续学习
                            </Button>
                          </Space>
                        }
                        hoverable
                        style={{ 
                          background: progress > 0 ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'linear-gradient(135deg, #1890ff 0%, #1890ff 100%)',
                          color: 'white'
                        }}
                      >
                        <Row gutter={16}>
                          <Col span={12}>
                            <Statistic
                              title="学科"
                              value={course.subject}
                              valueStyle={{ color: 'white', fontSize: 16 }}
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="年级"
                              value={`${course.grade_level}年级`}
                              valueStyle={{ color: 'white', fontSize: 16 }}
                            />
                          </Col>
                        </Row>
                        <Progress
                          percent={Math.round(progress * 100)}
                          status="active"
                          strokeColor="white"
                          style={{ marginTop: 16 }}
                        />
                      </Card>
                    </List.Item>
                  );
                }}
              />
            ) : (
              <Empty 
                description="暂无课程" 
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button type="primary" onClick={() => navigate('/courses')}>
                  浏览课程
                </Button>
              </Empty>
            )}
          </Card>

          {recentTasks.length > 0 && (
            <Card 
              title={
                <Space>
                  <ClockCircleOutlined />
                  <span>待完成任务</span>
                </Space>
              }
              style={{ marginTop: 16 }}
            >
              <List
                dataSource={recentTasks}
                renderItem={(task) => (
                  <List.Item
                    actions={[
                      <Button 
                        type="primary" 
                        size="small"
                        key="do"
                        onClick={() => handleQuickTask(task)}
                      >
                        {task.type === 'practice' ? '练习' : task.type === 'review' ? '复习' : '学习'}
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta
                      title={task.title}
                      description={task.description || `类型: ${task.type}`}
                    />
                  </List.Item>
                )}
              />
            </Card>
          )}
        </Col>

        <Col xs={24} lg={8}>
          <Card 
            title={
              <Space>
                <FileTextOutlined />
                <span>待复习</span>
              </Space>
            }
            extra={
              completedGoals > 0 && (
                <Statistic 
                  value={completedGoals} 
                  suffix="个目标已完成" 
                  valueStyle={{ fontSize: 14 }}
                />
              )
            }
          >
            {pendingReviews.length > 0 ? (
              <List
                size="small"
                dataSource={pendingReviews}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Button 
                        type="link" 
                        size="small"
                        key="review"
                        onClick={() => handleReview(item)}
                      >
                        复习
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta 
                      title={item.title}
                      description={item.description}
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty 
                description="暂无待复习内容" 
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </Card>
        </Col>
      </Row>
    </Spin>
  );
}
