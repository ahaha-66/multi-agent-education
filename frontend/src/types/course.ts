export interface Course {
  id: string;
  code: string;
  name: string;
  subject: string;
  grade_level: number;
  description: string;
}

export interface Chapter {
  id: string;
  name: string;
  order_index: number;
  knowledge_points: KnowledgePoint[];
}

export interface KnowledgePoint {
  id: string;
  code: string;
  name: string;
  order_index: number;
}

export interface CourseCatalog {
  course_id: string;
  chapters: Chapter[];
}

export interface KnowledgeGraphNode {
  id: string;
  code: string;
  name: string;
  difficulty: number;
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface KnowledgeGraph {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}
