import { useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Card, Button, Spin, Typography } from 'antd';
import { ArrowLeftOutlined, PlayCircleOutlined } from '@ant-design/icons';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchKnowledgeGraph } from '../store/slices/courseSlice';

const { Title, Text } = Typography;

function CustomNode({ data }: { data: any }) {
  const bgColor = data.isMastered ? '#52c41a' : data.isStarted ? '#1890ff' : '#ff9a3c';
  
  return (
    <div
      style={{
        padding: 16,
        background: bgColor,
        color: '#fff',
        borderRadius: 8,
        textAlign: 'center',
        minWidth: 100,
      }}
    >
      <Handle type="target" position={Position.Top} />
      <div>{data.name}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

const nodeTypes = {
  custom: CustomNode,
};

export default function KnowledgeGraphPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { knowledgeGraph, loading } = useAppSelector((state) => state.course);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  useEffect(() => {
    if (courseId) {
      dispatch(fetchKnowledgeGraph(courseId));
    }
  }, [dispatch, courseId]);

  useEffect(() => {
    if (knowledgeGraph) {
      const newNodes: Node[] = knowledgeGraph.nodes.map((node, index) => ({
        id: node.id,
        type: 'custom',
        position: { x: (index % 3) * 250, y: Math.floor(index / 3) * 150 },
        data: {
          name: node.name,
          isMastered: Math.random() > 0.5,
          isStarted: Math.random() > 0.3,
        },
      }));

      const newEdges: Edge[] = knowledgeGraph.edges.map((edge) => ({
        id: `e-${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
      }));

      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [knowledgeGraph, setNodes, setEdges]);

  const handleGoBack = () => {
    navigate(`/courses/${courseId}`);
  };

  const handleStartPractice = () => {
    navigate(`/courses/${courseId}/practice`);
  };

  return (
    <Spin spinning={loading}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={handleGoBack}>
            返回课程
          </Button>
        </Col>

        <Col span={18}>
          <Card title="知识图谱">
            <div style={{ height: 600 }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
              >
                <Background />
                <Controls />
                <MiniMap />
              </ReactFlow>
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card title="说明">
            <ul>
              <li>
                <div
                  style={{
                    width: 16,
                    height: 16,
                    background: '#52c41a',
                    display: 'inline-block',
                    marginRight: 8,
                  }}
                />
                已掌握
              </li>
              <li>
                <div
                  style={{
                    width: 16,
                    height: 16,
                    background: '#1890ff',
                    display: 'inline-block',
                    marginRight: 8,
                  }}
                />
                进行中
              </li>
              <li>
                <div
                  style={{
                    width: 16,
                    height: 16,
                    background: '#ff9a3c',
                    display: 'inline-block',
                    marginRight: 8,
                  }}
                />
                未开始
              </li>
            </ul>

            <div style={{ marginTop: 24 }}>
              <Button
                type="primary"
                block
                size="large"
                icon={<PlayCircleOutlined />}
                onClick={handleStartPractice}
              >
                开始练习
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </Spin>
  );
}
