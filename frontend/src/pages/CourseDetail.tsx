import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Row, 
  Col, 
  Card, 
  Button, 
  Progress, 
  Spin, 
  Tree, 
  Typography,
  Space,
  Tag,
  List,
  Empty,
  Statistic,
  Tooltip,
  Divider,
} from 'antd';
import { 
  ArrowLeftOutlined, 
  BranchesOutlined, 
  PlayCircleOutlined,
  BookOutlined,
  CheckCircleOutlined,
  StarOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import {
  fetchCourse,
  fetchCourseCatalog,
  fetchKnowledgeGraph,
  setCurrentCourse,
} from '../store/slices/courseSlice';
import { fetchCourseProgress } from '../store/slices/progressSlice';

const { Title, Text, Paragraph } = Typography;
const { DirectoryTree } = Tree;

export default function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { current: course, catalog, loading } = useAppSelector(
    (state) => state.course
  );
  const { courses: courseProgressList } = useAppSelector(
    (state) => state.progress
  );

  useEffect(() => {
    if (courseId) {
      dispatch(fetchCourse(courseId));
      dispatch(fetchCourseCatalog(courseId));
      dispatch(fetchCourseProgress({ learnerId, courseId }));
    }
  }, [dispatch, courseId, learnerId]);

  const courseProgress = courseProgressList.find((c) => c.course_id === courseId);
  const overallProgress = courseProgress?.overall_progress || 0;

  const handleGoBack = () => {
    navigate('/courses');
  };

  const handleSelectKnowledgePoint = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length > 0) {
      navigate(`/courses/${courseId}/practice?kp=${selectedKeys[0]}`);
    }
  };

  const handleStartPractice = () => {
    if (courseId) {
      navigate(`/courses/${courseId}/practice`);
    }
  };

  const handleGoToKnowledgeGraph = () => {
    if (courseId) {
      dispatch(fetchKnowledgeGraph(courseId));
      navigate(`/courses/${courseId}/knowledge-graph`);
    }
  };

  const treeData = catalog?.chapters.map((chapter) => ({
    key: chapter.id,
    title: (
      <Space>
        <BookOutlined />
        <Text strong>{chapter.name}</Text>
        <Tag color="blue">{chapter.knowledge_points.length}个知识点</Tag>
      </Space>
    ),
    children: chapter.knowledge_points.map((kp) => ({
      key: kp.id,
      title: (
        <Space>
          <Text>{kp.name}</Text>
          <Tooltip title={`难度: ${kp.difficulty}`}>
            <StarOutlined style={{ color: '#faad14' }} />
          </Tooltip>
        </Space>
      ),
    })),
  }));

  const totalKnowledgePoints = catalog?.chapters.reduce(
    (sum, ch) => sum + ch.knowledge_points.length, 
    0
  ) || 0;

  const masteredPoints = courseProgress?.knowledge_mastery?.filter(
    (km: any) => km.mastery > 0.7
  )?.length || 0;

  return (
    <Spin spinning={loading} tip="加载课程信息...">
      <div style={{ marginBottom: 16 }}>
        <Button 
          type="text" 
          icon={<ArrowLeftOutlined />} 
          onClick={handleGoBack}
        >
          返回课程列表
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card
            title={
              <Space>
                <BookOutlined />
                <span>{course?.name || '课程详情'}</span>
              </Space>
            }
            extra={
              <Space>
                <Button
                  icon={<BranchesOutlined />}
                  onClick={handleGoToKnowledgeGraph}
                >
                  知识图谱
                </Button>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={handleStartPractice}
                >
                  开始练习
                </Button>
              </Space>
            }
          >
            {course && (
              <>
                <div style={{ marginBottom: 16 }}>
                  <Space wrap>
                    <Tag color="blue">{course.subject}</Tag>
                    {course.grade_level && (
                      <Tag color="green">{course.grade_level}年级</Tag>
                    )}
                    {course.description && (
                      <Text type="secondary">{course.description}</Text>
                    )}
                  </Space>
                </div>

                <Card 
                  type="inner" 
                  title="课程章节"
                  style={{ marginBottom: 16 }}
                >
                  {catalog && catalog.chapters.length > 0 ? (
                    <DirectoryTree
                      treeData={treeData}
                      onSelect={(keys) => handleSelectKnowledgePoint(keys)}
                      showLine={{ showLeafIcon: false }}
                      blockNode
                    />
                  ) : (
                    <Empty description="暂无章节信息" />
                  )}
                </Card>
              </>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="学习进度">
            <Card.Meta
              title={
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={Math.round(overallProgress * 100)}
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                    format={(percent) => (
                      <div>
                        <div style={{ fontSize: 24, fontWeight: 'bold' }}>
                          {percent}%
                        </div>
                        <div style={{ fontSize: 12 }}>完成度</div>
                      </div>
                    )}
                  />
                </div>
              }
            />
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={12}>
                <Statistic 
                  title="章节数" 
                  value={catalog?.chapters.length || 0}
                  prefix={<BookOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="知识点" 
                  value={totalKnowledgePoints}
                  prefix={<TeamOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
            </Row>

            <Divider />

            <Statistic 
              title="已掌握" 
              value={masteredPoints}
              suffix={`/ ${totalKnowledgePoints}`}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />

            <Divider />

            <Button 
              type="primary" 
              block 
              icon={<PlayCircleOutlined />}
              onClick={handleStartPractice}
              size="large"
            >
              开始练习
            </Button>
          </Card>

          <Card 
            title="快速入口" 
            style={{ marginTop: 16 }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button 
                block 
                icon={<BranchesOutlined />}
                onClick={handleGoToKnowledgeGraph}
              >
                查看知识图谱
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </Spin>
  );
}
