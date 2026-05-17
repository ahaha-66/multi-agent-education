import { useEffect } from 'react';
import { Row, Col, Card, Button, Spin, List, Tag } from 'antd';
import { BookOutlined, BookFilled } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchCourses } from '../store/slices/courseSlice';
import { fetchOverallProgress } from '../store/slices/progressSlice';

export default function CourseListPage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { list: courses, loading: coursesLoading } = useAppSelector(
    (state) => state.course
  );
  const { overall } = useAppSelector((state) => state.progress);

  useEffect(() => {
    dispatch(fetchCourses());
    dispatch(fetchOverallProgress(learnerId));
  }, [dispatch, learnerId]);

  const handleCourseClick = (courseId: string) => {
    navigate(`/courses/${courseId}`);
  };

  const getCourseProgress = (courseId: string) => {
    const courseProgress = overall?.courses.find((c) => c.course_id === courseId);
    return courseProgress?.overall_progress || 0;
  };

  return (
    <Spin spinning={coursesLoading}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="课程列表">
            <List
              grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4 }}
              dataSource={courses}
              renderItem={(course) => {
                const progress = getCourseProgress(course.id);
                return (
                  <List.Item>
                    <Card
                      hoverable
                      cover={
                        <div
                          style={{
                            height: 120,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: '#f0f2f5',
                          }}
                        >
                          <BookFilled style={{ fontSize: 48, color: '#1890ff' }} />
                        </div>
                      }
                      actions={[
                        <Button
                          type="primary"
                          key="learn"
                          onClick={() => handleCourseClick(course.id)}
                        >
                          开始学习
                        </Button>,
                      ]}
                    >
                      <Card.Meta
                        title={course.name}
                        description={
                          <div>
                            <Tag color="blue">{course.subject}</Tag>
                            <Tag color="green">{course.grade_level}年级</Tag>
                            <p style={{ marginTop: 8 }}>
                              进度: {Math.round(progress * 100)}%
                            </p>
                          </div>
                        }
                      />
                    </Card>
                  </List.Item>
                );
              }}
            />
          </Card>
        </Col>
      </Row>
    </Spin>
  );
}
