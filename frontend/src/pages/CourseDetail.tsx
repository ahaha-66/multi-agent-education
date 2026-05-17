import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Card, Button, Progress, Spin, Tree, Typography } from 'antd';
import { ArrowLeftOutlined, BranchesOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import {
  fetchCourse,
  fetchCourseCatalog,
  fetchKnowledgeGraph,
  setCurrentCourse,
} from '../store/slices/courseSlice';
import { fetchCourseProgress } from '../store/slices/progressSlice';

const { Title, Text } = Typography;
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

  const handleGoToKnowledgeGraph = () => {
    if (courseId) {
      dispatch(fetchKnowledgeGraph(courseId));
      navigate(`/courses/${courseId}/knowledge-graph`);
    }
  };

  const treeData = catalog?.chapters.map((chapter) => ({
    key: chapter.id,
    title: chapter.name,
    children: chapter.knowledge_points.map((kp) => ({
      key: kp.id,
      title: kp.name,
    })),
  }));

  return (
    <Spin spinning={loading}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={handleGoBack}>
            返回课程列表
          </Button>
        </Col>

        <Col span={16}>
          <Card
            title={course?.name}
            extra={
              <Button
                type="primary"
                icon={<BranchesOutlined />}
                onClick={handleGoToKnowledgeGraph}
              >
                知识图谱
              </Button>
            }
          >
            <Row gutter={16}>
              <Col span={24}>
                <Text strong>总进度:</Text>
                <Progress
                  percent={Math.round(overallProgress * 100)}
                  style={{ marginLeft: 8 }}
                />
                <p style={{ marginTop: 8 }}>
                  完成章节: {courseProgress?.completed_chapters} / {courseProgress?.total_chapters}
                </p>
                <p>
                  掌握知识点: {courseProgress?.mastered_knowledge_points} / {courseProgress?.total_knowledge_points}
                </p>
              </Col>
            </Row>

            <Title level={4} style={{ marginTop: 24 }}>
              课程目录
            </Title>
            {treeData && treeData.length > 0 ? (
              <DirectoryTree
                multiple
                defaultExpandAll
                onSelect={handleSelectKnowledgePoint}
                treeData={treeData}
              />
            ) : (
              <Text type="secondary">暂无目录数据</Text>
            )}
          </Card>
        </Col>

        <Col span={8}>
          <Card title="快速开始">
            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              block
              onClick={() => navigate(`/courses/${courseId}/practice`)}
            >
              开始练习
            </Button>
            <p style={{ marginTop: 16 }}>
              智能推荐适合你当前水平的练习题
            </p>
          </Card>
        </Col>
      </Row>
    </Spin>
  );
}
