import { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import {
  Row,
  Col,
  Card,
  Button,
  Radio,
  Result,
  Spin,
  Typography,
  Space,
  Divider,
} from 'antd';
import {
  ArrowLeftOutlined,
  CheckOutlined,
  CloseOutlined,
  BulbOutlined,
  RightOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import {
  fetchNextExercise,
  submitAnswer,
  setAnswer,
  clearAnswer,
  incrementHintLevel,
} from '../store/slices/exerciseSlice';

const { Title, Text, Paragraph } = Typography;
const { Group: RadioGroup } = Radio;

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

  const handleAnswerChange = (e: any) => {
    dispatch(setAnswer(e.target.value));
  };

  const handleSubmitAnswer = () => {
    if (exercise) {
      dispatch(
        submitAnswer({
          request: {
            exercise_id: exercise.id,
            answer: answer,
          },
          learnerId,
        })
      );
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
    dispatch(incrementHintLevel());
  };

  const handleGoBack = () => {
    navigate(`/courses/${courseId}`);
  };

  const currentHint =
    exercise && hintLevel > 0
      ? exercise.hint_levels.find((h) => h.level === hintLevel)
      : null;

  return (
    <Spin spinning={loading}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={handleGoBack}>
            返回课程
          </Button>
        </Col>

        {exercise && (
          <>
            <Col span={24}>
              <Card
                title={`${exercise.code} - 难度: ${'⭐'.repeat(exercise.difficulty)}`}
              >
                <Title level={4}>{exercise.content.stem}</Title>

                {exercise.type === 'single_choice' &&
                  exercise.content.options && (
                    <RadioGroup
                      value={answer}
                      onChange={handleAnswerChange}
                      disabled={!!feedback}
                    >
                      <Space direction="vertical" style={{ width: '100%' }}>
                        {exercise.content.options.map((option, index) => (
                          <Radio key={index} value={option.value}>
                            {option.label}. {option.value}
                          </Radio>
                        ))}
                      </Space>
                    </RadioGroup>
                  )}

                {currentHint && (
                  <>
                    <Divider />
                    <Card
                      type="inner"
                      title={
                        <Space>
                          <BulbOutlined />
                          提示 {hintLevel}
                        </Space>
                      }
                    >
                      <Paragraph>{currentHint.hint}</Paragraph>
                    </Card>
                  </>
                )}

                <Space style={{ marginTop: 24 }}>
                  {!feedback && (
                    <>
                      <Button
                        type="default"
                        icon={<BulbOutlined />}
                        disabled={hintLevel >= 3}
                        onClick={handleRequestHint}
                      >
                        获取提示
                      </Button>
                      <Button
                        type="primary"
                        icon={<CheckOutlined />}
                        onClick={handleSubmitAnswer}
                        disabled={!answer}
                        loading={isSubmitting}
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
                    >
                      下一题
                    </Button>
                  )}
                </Space>
              </Card>
            </Col>

            {feedback && (
              <Col span={24}>
                <Result
                  status={feedback.is_correct ? 'success' : 'error'}
                  title={
                    feedback.is_correct ? (
                      <Space>
                        <CheckOutlined />
                        回答正确
                      </Space>
                    ) : (
                      <Space>
                        <CloseOutlined />
                        回答错误
                      </Space>
                    )
                  }
                  message={`正确答案: ${feedback.correct_answer?.value || feedback.correct_answer}`}
                  extra={
                    feedback.analysis && (
                      <Card type="inner" title="解析">
                        <Paragraph>{feedback.analysis.text}</Paragraph>
                        {feedback.analysis.key_point && (
                          <Paragraph type="secondary" style={{ marginTop: 8 }}>
                            关键点: {feedback.analysis.key_point}
                          </Paragraph>
                        )}
                      </Card>
                    )
                  }
                />
              </Col>
            )}
          </>
        )}
      </Row>
    </Spin>
  );
}
