import { useEffect, useState } from 'react';
import { Row, Col, Card, Button, Spin, List, Tag, Empty, message, Typography } from 'antd';
import { BookOutlined, BookFilled, PlayCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchCourses } from '../store/slices/courseSlice';
import { fetchOverallProgress } from '../store/slices/progressSlice';
import type { Course } from '../types/course';

const { Title, Text } = Typography;

export default function CourseListPage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { list: courses, loading: coursesLoading, error } = useAppSelector(
    (state) => state.course
  );
  const { overall } = useAppSelector((state) => state.progress);
  const [displayedCourses, setDisplayedCourses] = useState<Course[]>([]);
  const [visibleCount, setVisibleCount] = useState(6);

  useEffect(() => {
    dispatch(fetchCourses());
    dispatch(fetchOverallProgress(learnerId));
  }, [dispatch, learnerId]);

  useEffect(() => {
    setDisplayedCourses(courses.slice(0, visibleCount));
  }, [courses, visibleCount]);

  useEffect(() => {
    if (error) {
      message.error('加载课程失败，请重试');
    }
  }, [error]);

  const handleCourseClick = (courseId: string) => {
    navigate(`/courses/${courseId}`);
  };

  const getCourseProgress = (courseId: string) => {
    const courseProgress = overall?.courses.find((c) => c.course_id === courseId);
    return courseProgress?.overall_progress || 0;
  };

  const getSubjectColor = (subject: string) => {
    const colorMap: Record<string, string> = {
      math: 'blue',
      chinese: 'red',
      english: 'green',
      physics: 'purple',
      chemistry: 'orange',
      biology: 'cyan',
      history: 'gold',
      geography: 'lime',
    };
    return colorMap[subject.toLowerCase()] || 'blue';
  };

  const handleLoadMore = () => {
    setVisibleCount(prev => prev + 6);
  };

  const getProgressColor = (progress: number) => {
    if (progress === 0) return '#1890ff';
    if (progress < 0.3) return '#faad14';
    if (progress < 0.7) return '#52c41a';
    return '#722ed1';
  };

  return (
    <Spin spinning={coursesLoading} tip="加载课程中...">
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card 
            title={
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span>全部课程</span>
                <Tag color="processing">{courses.length} 个课程</Tag>
              </div>
            }
          >
            {error ? (
              <Empty 
                description={
                  <div>
                    <Text type="danger">加载失败</Text>
                    <br />
                    <Button type="link" onClick={() => dispatch(fetchCourses())}>
                      点击重试
                    </Button>
                  </div>
                }
              />
            ) : displayedCourses.length > 0 ? (
              <>
                <List
                  grid={{ 
                    gutter: 16, 
                    xs: 1, 
                    sm: 1, 
                    md: 2, 
                    lg: 3, 
                    xl: 3,
                    xxl: 4 
                  }}
                  dataSource={displayedCourses}
                  renderItem={(course) => {
                    const progress = getCourseProgress(course.id);
                    const hasProgress = progress > 0;
                    
                    return (
                      <List.Item>
                        <Card
                          hoverable
                          className="course-card"
                          style={{
                            height: '100%',
                            background: hasProgress 
                              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                              : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                            transition: 'all 0.3s ease',
                            border: hasProgress ? '2px solid #667eea' : '2px solid transparent',
                          }}
                          bodyStyle={{ 
                            height: '100%', 
                            display: 'flex', 
                            flexDirection: 'column',
                            color: hasProgress ? 'white' : 'inherit'
                          }}
                          actions={[
                            <Button
                              type={hasProgress ? 'default' : 'primary'}
                              icon={<PlayCircleOutlined />}
                              key="learn"
                              onClick={() => handleCourseClick(course.id)}
                              style={{ 
                                width: '100%',
                                background: hasProgress ? 'rgba(255,255,255,0.9)' : undefined,
                                borderColor: hasProgress ? 'white' : undefined,
                              }}
                            >
                              {hasProgress ? '继续学习' : '开始学习'}
                            </Button>,
                          ]}
                        >
                          <div
                            style={{
                              height: 100,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              background: hasProgress ? 'rgba(255,255,255,0.2)' : '#f0f2f5',
                              borderRadius: 8,
                              marginBottom: 12,
                            }}
                          >
                            <BookFilled 
                              style={{ 
                                fontSize: 48, 
                                color: hasProgress ? 'white' : '#1890ff' 
                              }} 
                            />
                          </div>
                          
                          <div style={{ flex: 1 }}>
                            <Title 
                              level={5} 
                              style={{ 
                                margin: '0 0 8px 0',
                                color: hasProgress ? 'white' : undefined,
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis'
                              }}
                            >
                              {course.name}
                            </Title>
                            
                            <div style={{ marginBottom: 8 }}>
                              <Tag color={getSubjectColor(course.subject)}>
                                {course.subject}
                              </Tag>
                              {course.grade_level && (
                                <Tag color="default">
                                  {course.grade_level}年级
                                </Tag>
                              )}
                            </div>
                            
                            {course.description && (
                              <Text 
                                style={{ 
                                  color: hasProgress ? 'rgba(255,255,255,0.8)' : undefined,
                                  display: '-webkit-box',
                                  WebkitLineClamp: 2,
                                  WebkitBoxOrient: 'vertical',
                                  overflow: 'hidden',
                                  fontSize: 12
                                }}
                              >
                                {course.description}
                              </Text>
                            )}
                          </div>
                          
                          <div style={{ marginTop: 12 }}>
                            <div style={{ 
                              display: 'flex', 
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: 4,
                              color: hasProgress ? 'rgba(255,255,255,0.9)' : undefined
                            }}>
                              <Text style={{ fontSize: 12, color: hasProgress ? 'rgba(255,255,255,0.8)' : undefined }}>
                                学习进度
                              </Text>
                              <Text style={{ 
                                fontSize: 12, 
                                fontWeight: 'bold',
                                color: hasProgress ? 'white' : undefined 
                              }}>
                                {Math.round(progress * 100)}%
                              </Text>
                            </div>
                            <div 
                              style={{ 
                                width: '100%', 
                                height: 6, 
                                background: hasProgress ? 'rgba(255,255,255,0.3)' : '#e8e8e8',
                                borderRadius: 3,
                                overflow: 'hidden'
                              }}
                            >
                              <div
                                style={{
                                  width: `${Math.round(progress * 100)}%`,
                                  height: '100%',
                                  background: getProgressColor(progress),
                                  transition: 'width 0.3s ease'
                                }}
                              />
                            </div>
                          </div>
                        </Card>
                      </List.Item>
                    );
                  }}
                />
                
                {courses.length > visibleCount && (
                  <div style={{ textAlign: 'center', marginTop: 24 }}>
                    <Button 
                      onClick={handleLoadMore}
                      icon={<BookOutlined />}
                    >
                      加载更多课程
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <Empty 
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  <div>
                    <Text>暂无课程</Text>
                    <br />
                    <Button type="primary" onClick={() => navigate('/')}>
                      返回首页
                    </Button>
                  </div>
                }
              />
            )}
          </Card>
        </Col>
      </Row>
      
      <style>{`
        .course-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }
        
        @media (max-width: 768px) {
          .course-card {
            margin-bottom: 16px;
          }
        }
      `}</style>
    </Spin>
  );
}
