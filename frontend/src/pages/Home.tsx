import { useEffect } from 'react';
import { Row, Col, Card, Button, Statistic, Progress, Spin, List } from 'antd';
import { BookOutlined, ClockCircleOutlined, FileTextOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchOverallProgress } from '../store/slices/progressSlice';
import { fetchCourses } from '../store/slices/courseSlice';

export default function HomePage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { overall, loading: progressLoading } = useAppSelector(
    (state) => state.progress
  );
  const { list: courses, loading: coursesLoading } = useAppSelector(
    (state) => state.course
  );

  useEffect(() => {
    dispatch(fetchOverallProgress(learnerId));
    dispatch(fetchCourses());
  }, [dispatch, learnerId]);

  const handleContinueLearning = (courseId: string) => {
    navigate(`/courses/${courseId}`);
  };

  const totalProgress = overall?.overall_progress || 0;
  const totalMistakes = 0;

  return (
    <Spin spinning={progressLoading || coursesLoading}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="学习概览">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="总进度"
                  value={Math.round(totalProgress * 100)}
                  suffix="%"
                  valueStyle={{ color: totalProgress > 0.5 ? '#3f8600' : '#1890ff' }}
                />
                <Progress percent={Math.round(totalProgress * 100)} />
              </Col>
              <Col span={6}>
                <Statistic
                  title="错题数量"
                  value={totalMistakes}
                  prefix={<FileTextOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="学习课程"
                  value={courses.length}
                  prefix={<BookOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="学习天数"
                  value={1}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        <Col span={16}>
          <Card title="继续学习">
            <List
              grid={{ gutter: 16, column: 2 }}
              dataSource={courses.slice(0, 2)}
              renderItem={(course) => (
                <List.Item>
                  <Card
                    title={course.name}
                    hoverable
                    extra={
                      <Button
                        type="primary"
                        onClick={() => handleContinueLearning(course.id)}
                      >
                        继续学习
                      </Button>
                    }
                  >
                    <p>学科: {course.subject}</p>
                    <p>年级: {course.grade_level}年级</p>
                    <Progress
                      percent={Math.round(
                        (overall?.courses.find((c) => c.course_id === course.id)
                          ?.overall_progress || 0) * 100
                      )}
                      status="active"
                    />
                  </Card>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col span={8}>
          <Card title="待复习">
            <List
              dataSource={[
                { id: '1', name: '有理数', time: '2小时前' },
                { id: '2', name: '正数和负数', time: '1天前' },
              ]}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button type="link" key="review">
                      复习
                    </Button>,
                  ]}
                >
                  <List.Item.Meta title={item.name} description={item.time} />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </Spin>
  );
}
