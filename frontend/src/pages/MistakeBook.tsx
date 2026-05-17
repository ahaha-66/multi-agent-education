import { useEffect, useState } from 'react';
import {
  Row,
  Col,
  Card,
  Table,
  Button,
  Tag,
  Space,
  Pagination,
  Select,
  Modal,
  Typography,
  Divider,
} from 'antd';
import { FileTextOutlined, EyeOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../store';
import {
  fetchMistakes,
  fetchMistakeDetail,
  resolveMistake,
  fetchMistakeStatistics,
} from '../store/slices/mistakeSlice';

const { Title, Text } = Typography;
const { Option } = Select;

export default function MistakeBookPage() {
  const dispatch = useAppDispatch();
  const learnerId = useAppSelector((state) => state.user.id);
  const { list: mistakeData, detail: mistakeDetail, statistics, loading } =
    useAppSelector((state) => state.mistake);

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [selectedResolved, setSelectedResolved] = useState<boolean | undefined>(
    undefined
  );
  const [detailModalOpen, setDetailModalOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchMistakes({ learnerId }));
    dispatch(fetchMistakeStatistics(learnerId));
  }, [dispatch, learnerId]);

  const handlePageChange = (page: number, size: number) => {
    setCurrentPage(page);
    setPageSize(size);
    dispatch(
      fetchMistakes({
        learnerId,
        params: {
          isResolved: selectedResolved,
          page,
          pageSize: size,
        },
      })
    );
  };

  const handleResolvedFilterChange = (value: boolean | undefined) => {
    setSelectedResolved(value);
    dispatch(
      fetchMistakes({
        learnerId,
        params: {
          isResolved: value,
          page: 1,
          pageSize,
        },
      })
    );
  };

  const handleViewDetail = (mistakeId: string) => {
    dispatch(fetchMistakeDetail({ learnerId, mistakeId }));
    setDetailModalOpen(true);
  };

  const handleResolve = (mistakeId: string) => {
    dispatch(resolveMistake({ learnerId, mistakeId }));
  };

  const columns = [
    {
      title: '错题编号',
      dataIndex: 'exercise_code',
      key: 'exercise_code',
    },
    {
      title: '知识点',
      dataIndex: 'knowledge_point_name',
      key: 'knowledge_point_name',
    },
    {
      title: '错误次数',
      dataIndex: 'wrong_count',
      key: 'wrong_count',
    },
    {
      title: '首次错误时间',
      dataIndex: 'first_wrong_at',
      key: 'first_wrong_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '状态',
      dataIndex: 'is_resolved',
      key: 'is_resolved',
      render: (resolved: boolean) => (
        <Tag color={resolved ? 'green' : 'red'}>
          {resolved ? '已解决' : '未解决'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record.id)}
          >
            查看
          </Button>
          {!record.is_resolved && (
            <Button
              type="link"
              size="small"
              icon={<CheckCircleOutlined />}
              onClick={() => handleResolve(record.id)}
            >
              标记解决
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      <Col span={6}>
        <Card title="错题统计">
          <Row gutter={[8, 8]}>
            <Col span={24}>
              <Statistic
                title="总错题数"
                value={statistics?.total_mistakes || 0}
              />
            </Col>
            <Col span={24}>
              <Statistic
                title="已解决"
                value={statistics?.resolved_mistakes || 0}
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
            <Col span={24}>
              <Statistic
                title="未解决"
                value={statistics?.unresolved_mistakes || 0}
                valueStyle={{ color: '#cf1322' }}
              />
            </Col>
          </Row>
        </Card>
      </Col>

      <Col span={18}>
        <Card
          title="错题列表"
          extra={
            <Select
              placeholder="筛选状态"
              style={{ width: 120 }}
              allowClear
              value={selectedResolved}
              onChange={handleResolvedFilterChange}
            >
              <Option value={false}>未解决</Option>
              <Option value={true}>已解决</Option>
            </Select>
          }
        >
          <Table
            dataSource={mistakeData?.mistakes || []}
            columns={columns}
            rowKey="id"
            pagination={false}
            loading={loading}
          />
          <Divider />
          <Pagination
            current={currentPage}
            pageSize={pageSize}
            total={mistakeData?.total || 0}
            onChange={handlePageChange}
            style={{ textAlign: 'center' }}
          />
        </Card>
      </Col>

      <Modal
        title="错题详情"
        open={detailModalOpen}
        onCancel={() => setDetailModalOpen(false)}
        footer={null}
        width={800}
      >
        {mistakeDetail && (
          <div>
            <Title level={5}>题目内容</Title>
            <Card size="small" style={{ marginBottom: 16 }}>
              <Text>{mistakeDetail.content.stem}</Text>
            </Card>

            <Row gutter={16}>
              <Col span={12}>
                <Title level={5}>错误答案</Title>
                <Card size="small" type="inner" style={{ background: '#fff2f0' }}>
                  <Text type="danger">
                    {mistakeDetail.last_attempt_answer}
                  </Text>
                </Card>
              </Col>
              <Col span={12}>
                <Title level={5}>正确答案</Title>
                <Card size="small" type="inner" style={{ background: '#f6ffed' }}>
                  <Text type="success">
                    {mistakeDetail.correct_answer}
                  </Text>
                </Card>
              </Col>
            </Row>

            {mistakeDetail.analysis && (
              <>
                <Title level={5} style={{ marginTop: 16 }}>
                  解析
                </Title>
                <Card size="small">
                  <Text>{mistakeDetail.analysis}</Text>
                </Card>
              </>
            )}

            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Text type="secondary">
                  知识点: {mistakeDetail.knowledge_point_name}
                </Text>
              </Col>
              <Col span={12}>
                <Text type="secondary">
                  错误次数: {mistakeDetail.wrong_count}
                </Text>
              </Col>
            </Row>
          </div>
        )}
      </Modal>
    </Row>
  );
}

function Statistic({ title, value, valueStyle }: { title: string; value: number; valueStyle?: React.CSSProperties }) {
  return (
    <div>
      <Text type="secondary">{title}</Text>
      <div style={{ fontSize: 24, fontWeight: 'bold', marginTop: 4, ...valueStyle }}>
        {value}
      </div>
    </div>
  );
}
