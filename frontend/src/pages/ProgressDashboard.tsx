import { useEffect } from 'react';
import { Row, Col, Card, Progress, Typography, Spin, Statistic } from 'antd';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchOverallProgress } from '../store/slices/progressSlice';
import ReactECharts from 'echarts-for-react';

const { Title, Text } = Typography;

export default function ProgressDashboardPage() {
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { overall, loading } = useAppSelector((state) => state.progress);

  useEffect(() => {
    dispatch(fetchOverallProgress(learnerId));
  }, [dispatch, learnerId]);

  const totalProgress = overall?.overall_progress || 0;
  const totalCourses = overall?.total_courses || 0;
  const completedCourses = overall?.completed_courses || 0;

  const getCourseChartOption = () => {
    if (!overall?.courses) return {};
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
      },
      xAxis: {
        type: 'category',
        data: overall.courses.map((c) => c.course_name),
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}%',
        },
      },
      series: [
        {
          name: '进度',
          type: 'bar',
          data: overall.courses.map((c) => Math.round(c.overall_progress * 100)),
          itemStyle: {
            color: (params: any) => {
              if (params.value >= 80) return '#52c41a';
              if (params.value >= 50) return '#1890ff';
              return '#ff9a3c';
            },
          },
        },
      ],
    };
  };

  return (
    <Spin spinning={loading}>
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card>
            <Statistic
              title="总进度"
              value={Math.round(totalProgress * 100)}
              suffix="%"
              valueStyle={{ color: totalProgress > 0.5 ? '#3f8600' : '#1890ff' }}
            />
            <Progress
              percent={Math.round(totalProgress * 100)}
              type="circle"
              style={{ margin: '24px 0' }}
            />
          </Card>
        </Col>

        <Col span={8}>
          <Card>
            <Statistic title="课程总数" value={totalCourses} />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">已完成: {completedCourses}</Text>
              <br />
              <Text type="secondary">进行中: {totalCourses - completedCourses}</Text>
            </div>
          </Card>
        </Col>

        <Col span={8}>
          <Card>
            <Statistic
              title="掌握知识点"
              value={
                overall?.courses.reduce(
                  (sum, c) => sum + c.mastered_knowledge_points,
                  0
                ) || 0
              }
            />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">
                总知识点:{' '}
                {overall?.courses.reduce(
                  (sum, c) => sum + c.total_knowledge_points,
                  0
                ) || 0}
              </Text>
            </div>
          </Card>
        </Col>

        <Col span={24}>
          <Card title="各课程进度">
            <ReactECharts
              option={getCourseChartOption()}
              style={{ height: 400 }}
            />
          </Card>
        </Col>

        {overall?.courses.map((course) => (
          <Col key={course.course_id} span={24}>
            <Card title={course.course_name}>
              <Row gutter={16}>
                <Col span={6}>
                  <Text strong>章节进度</Text>
                  <Progress
                    percent={Math.round(
                      (course.completed_chapters / course.total_chapters) * 100
                    )}
                    style={{ marginTop: 8 }}
                  />
                  <Text type="secondary" style={{ display: 'block', marginTop: 4 }}>
                    {course.completed_chapters} / {course.total_chapters}
                  </Text>
                </Col>
                <Col span={6}>
                  <Text strong>知识点掌握</Text>
                  <Progress
                    percent={Math.round(
                      (course.mastered_knowledge_points /
                        course.total_knowledge_points) *
                        100
                    )}
                    style={{ marginTop: 8 }}
                  />
                  <Text type="secondary" style={{ display: 'block', marginTop: 4 }}>
                    {course.mastered_knowledge_points} / {course.total_knowledge_points}
                  </Text>
                </Col>
                <Col span={12}>
                  <Text strong>章节详情</Text>
                  <div style={{ marginTop: 8 }}>
                    {course.chapters.map((chapter) => (
                      <div key={chapter.chapter_id} style={{ marginBottom: 8 }}>
                        <Text>{chapter.chapter_name}</Text>
                        <Progress
                          percent={Math.round(chapter.progress * 100)}
                          size="small"
                          style={{ marginTop: 4 }}
                        />
                      </div>
                    ))}
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>
        ))}
      </Row>
    </Spin>
  );
}
