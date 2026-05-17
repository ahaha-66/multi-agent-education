import { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import {
  Row,
  Col,
  Card,
  Button,
  Radio,
  Input,
  Result,
  Spin,
  Typography,
  Space,
  Divider,
  message,
  Progress,
  Tag,
  Tooltip,
} from 'antd';
import {
  ArrowLeftOutlined,
  CheckOutlined,
  CloseOutlined,
  BulbOutlined,
  RightOutlined,
  StarOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import {
  fetchNextExercise,
  submitAnswer,
  setAnswer,
  clearAnswer,
  incrementHintLevel,
} from '../store/slices/exerciseSlice';
import { fetchCourseProgress } from '../store/slices/progressSlice';
import { mistakeApi } from '../services/mistakeApi';

const { Title, Text, Paragraph } = Typography;
const { Group: RadioGroup } = Radio;
const { TextArea } = Input;

export default function PracticePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const {
    current: exercise,
    answer,
    feedback,
    isSubmitting,
    hintLevel,
    loading,
  } = useAppSelector((state) => state.exercise);
  const knowledgePointId = searchParams.get('kp');
  
  const [exerciseCount, setExerciseCount] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (courseId) {
      dispatch(
        fetchNextExercise({
          courseId,
          learnerId,
          knowledgePointId: knowledgePointId || undefined,
        })
      );
    }
  }, [dispatch, courseId, learnerId, knowledgePointId]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime]);

  useEffect(() => {
    if (feedback) {
      setExerciseCount(prev => prev + 1);
      if (feedback.is_correct) {
        setCorrectCount(prev => prev + 1);
      }
    }
  }, [feedback]);

  const handleAnswerChange = (e: any) => {
    dispatch(setAnswer(e.target.value));
  };

  const handleSubmitAnswer = async () => {
    if (exercise) {
      try {
        await dispatch(
          submitAnswer({
            request: {
              exercise_id: exercise.id,
              answer: answer,
            },
            learnerId,
          })
        ).unwrap();
        
        if (courseId) {
          dispatch(fetchCourseProgress({ learnerId, courseId }));
        }
      } catch (error) {
        message.error('提交答案失败，请重试');
      }
    }
  };

  const handleNextExercise = () => {
    dispatch(clearAnswer());
    if (courseId) {
      dispatch(
        fetchNextExercise({
          courseId,
          learnerId,
        })
      );
    }
  };

  const handleRequestHint = () => {
    if (hintLevel < 3) {
      dispatch(incrementHintLevel());
    } else {
      message.warning('已达到最大提示次数');
    }
  };

  const handleGoBack = () => {
    navigate(`/courses/${courseId}`);
  };

  const handleSkipExercise = () => {
    dispatch(clearAnswer());
    if (courseId) {
      dispatch(
        fetchNextExercise({
          courseId,
          learnerId,
        })
      );
    }
    message.info('已跳过当前题目');
  };

  const getDifficultyLabel = (difficulty: number) => {
    if (difficulty < 0.3) return { label: '简单', color: 'green' };
    if (difficulty < 0.6) return { label: '中等', color: 'orange' };
    return { label: '困难', color: 'red' };
  };

  const getTimeSpentFormatted = () => {
    const minutes = Math.floor(timeSpent / 60);
    const seconds = timeSpent % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const currentHint =
    exercise && hintLevel > 0
      ? exercise.hint_levels?.find((h: any) => h.level === hintLevel)
      : null;

  const difficulty = exercise ? getDifficultyLabel(exercise.difficulty) : { label: '未知', color: 'default' };

  return (
    <Spin spinning={loading} tip="加载题目中...">
      <div style={{ marginBottom: 16 }}>
        <Button 
          type="text" 
          icon={<ArrowLeftOutlined />} 
          onClick={handleGoBack}
        >
          返回课程
        </Button>
      </div>

      {exercise && (
        <>
          <Card
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Space>
                  <span>练习题</span>
                  <Tag color={difficulty.color}>{difficulty.label}</Tag>
                  <Tag icon={<StarOutlined />}>
                    {exercise.type === 'single_choice' ? '选择题' : 
                     exercise.type === 'fill_blank' ? '填空题' : 
                     exercise.type === 'true_false' ? '判断题' : '解答题'}
                  </Tag>
                </Space>
                <Space>
                  <Text type="secondary">
                    已用时: {getTimeSpentFormatted()}
                  </Text>
                  {exerciseCount > 0 && (
                    <Text>
                      正确率: <Text strong type={correctCount / exerciseCount > 0.6 ? 'success' : 'warning'}>
                        {Math.round(correctCount / exerciseCount * 100)}%
                      </Text>
                    </Text>
                  )}
                </Space>
              </div>
            }
            extra={
              <Tooltip title="跳过此题">
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={handleSkipExercise}
                  disabled={!!feedback}
                />
              </Tooltip>
            }
          >
            <Card
              type="inner"
              style={{ 
                background: '#fafafa',
                marginBottom: 24,
                border: '2px solid #e8e8e8',
                borderRadius: 8
              }}
            >
              <Title level={4} style={{ margin: 0 }}>
                {exercise.content.stem}
              </Title>
            </Card>

            {exercise.type === 'single_choice' &&
              exercise.content.options && (
                <RadioGroup
                  value={answer}
                  onChange={handleAnswerChange}
                  disabled={!!feedback}
                  style={{ width: '100%' }}
                >
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {exercise.content.options.map((option: any, index: number) => {
                      const isSelected = answer === option.value;
                      const isCorrect = feedback?.correct_answer?.value === option.value;
                      const showResult = !!feedback;
                      
                      return (
                        <Card
                          key={index}
                          style={{
                            width: '100%',
                            cursor: showResult ? 'default' : 'pointer',
                            transition: 'all 0.3s ease',
                            borderColor: showResult
                              ? isCorrect
                                ? '#52c41a'
                                : isSelected
                                  ? '#ff4d4f'
                                  : '#d9d9d9'
                              : isSelected
                                ? '#1890ff'
                                : '#d9d9d9',
                            background: showResult
                              ? isCorrect
                                ? '#f6ffed'
                                : isSelected
                                  ? '#fff2f0'
                                  : 'white'
                              : isSelected
                                ? '#e6f7ff'
                                : 'white',
                          }}
                          bodyStyle={{ padding: '12px 16px' }}
                          onClick={() => !showResult && dispatch(setAnswer(option.value))}
                        >
                          <Space>
                            <Radio value={option.value} disabled={!!feedback}>
                              <Text strong style={{ marginLeft: 8 }}>
                                {option.label}.
                              </Text>
                            </Radio>
                            <Text style={{ marginLeft: 8 }}>{option.value}</Text>
                            {showResult && isCorrect && (
                              <CheckOutlined style={{ color: '#52c41a', marginLeft: 8 }} />
                            )}
                            {showResult && isSelected && !isCorrect && (
                              <CloseOutlined style={{ color: '#ff4d4f', marginLeft: 8 }} />
                            )}
                          </Space>
                        </Card>
                      );
                    })}
                  </Space>
                </RadioGroup>
              )}

            {(exercise.type === 'fill_blank' || exercise.type === 'true_false' || !exercise.content.options) && (
              <div>
                <Text strong style={{ display: 'block', marginBottom: 8 }}>
                  请输入答案：
                </Text>
                {exercise.type === 'true_false' ? (
                  <RadioGroup
                    value={answer}
                    onChange={handleAnswerChange}
                    disabled={!!feedback}
                  >
                    <Space>
                      <Radio value="true">正确</Radio>
                      <Radio value="false">错误</Radio>
                    </Space>
                  </RadioGroup>
                ) : (
                  <Input
                    type="text"
                    value={answer}
                    onChange={(e) => dispatch(setAnswer(e.target.value))}
                    disabled={!!feedback}
                    placeholder="请输入答案"
                    size="large"
                    style={{ width: '100%', maxWidth: 400 }}
                    prefix={<BulbOutlined />}
                  />
                )}
              </div>
            )}

            {currentHint && (
              <>
                <Divider />
                <Card
                  type="inner"
                  style={{ 
                    background: '#fffbe6',
                    border: '1px solid #ffe58f'
                  }}
                  title={
                    <Space>
                      <BulbOutlined style={{ color: '#faad14' }} />
                      <span>提示 {hintLevel}</span>
                      <Tag color="warning">消耗积分</Tag>
                    </Space>
                  }
                >
                  <Paragraph style={{ margin: 0, fontSize: 16 }}>
                    {currentHint.hint}
                  </Paragraph>
                </Card>
              </>
            )}

            <Divider />

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                {!feedback && (
                  <Button
                    type="default"
                    icon={<BulbOutlined />}
                    disabled={hintLevel >= 3}
                    onClick={handleRequestHint}
                  >
                    获取提示 {hintLevel > 0 && `(${hintLevel}/3)`}
                  </Button>
                )}
              </Space>

              <Space>
                {!feedback && (
                  <>
                    <Button
                      type="primary"
                      icon={<CheckOutlined />}
                      onClick={handleSubmitAnswer}
                      disabled={!answer}
                      loading={isSubmitting}
                      size="large"
                    >
                      提交答案
                    </Button>
                  </>
                )}

                {feedback && (
                  <Button
                    type="primary"
                    icon={<RightOutlined />}
                    onClick={handleNextExercise}
                    size="large"
                  >
                    下一题
                  </Button>
                )}
              </Space>
            </div>
          </Card>

          {feedback && (
            <Card
              style={{
                marginTop: 16,
                borderColor: feedback.is_correct ? '#52c41a' : '#ff4d4f',
              }}
            >
              <Result
                status={feedback.is_correct ? 'success' : 'error'}
                title={
                  <Space>
                    {feedback.is_correct ? (
                      <>
                        <CheckOutlined style={{ color: '#52c41a' }} />
                        <span>回答正确！</span>
                        <Tag color="success">+1 积分</Tag>
                      </>
                    ) : (
                      <>
                        <CloseOutlined style={{ color: '#ff4d4f' }} />
                        <span>回答错误</span>
                        <Tag color="error">已记录到错题本</Tag>
                      </>
                    )}
                  </Space>
                }
                message={
                  <div>
                    <Text strong>正确答案: </Text>
                    <Text code style={{ fontSize: 16 }}>
                      {feedback.correct_answer?.value || String(feedback.correct_answer)}
                    </Text>
                  </div>
                }
                extra={
                  feedback.analysis && (
                    <Card type="inner" title="📚 题目解析" style={{ marginTop: 16 }}>
                      <Paragraph style={{ fontSize: 15 }}>
                        {feedback.analysis.text}
                      </Paragraph>
                      {feedback.analysis.key_point && (
                        <Paragraph type="secondary" style={{ marginTop: 12 }}>
                          <Text strong>💡 关键点: </Text>
                          <Tag color="blue">{feedback.analysis.key_point}</Tag>
                        </Paragraph>
                      )}
                    </Card>
                  )
                }
              />
            </Card>
          )}

          {exerciseCount > 0 && (
            <Card style={{ marginTop: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic 
                    title="已做题数" 
                    value={exerciseCount} 
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic 
                    title="正确数" 
                    value={correctCount} 
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic 
                    title="正确率" 
                    value={Math.round(correctCount / exerciseCount * 100)} 
                    suffix="%"
                    valueStyle={{ 
                      color: correctCount / exerciseCount > 0.6 ? '#52c41a' : '#faad14' 
                    }}
                  />
                </Col>
              </Row>
            </Card>
          )}
        </>
      )}

      {!loading && !exercise && (
        <Result
          status="info"
          title="练习完成"
          subTitle="恭喜你完成了本节练习！"
          extra={[
            <Button 
              type="primary" 
              key="review"
              icon={<BookOutlined />}
              onClick={() => navigate('/courses')}
            >
              返回课程列表
            </Button>,
            <Button 
              key="home"
              onClick={() => navigate('/')}
            >
              返回首页
            </Button>,
          ]}
        />
      )}
    </Spin>
  );
}
