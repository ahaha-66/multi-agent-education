export interface Course {
  id: string;
  code: string;
  name: string;
  subject: string;
  grade_level: number;
  description?: string;
  is_active?: boolean;
}

export interface KnowledgePoint {
  id: string;
  code: string;
  name: string;
  chapter_id: string;
  course_id: string;
  difficulty: number;
  description?: string;
  tags?: string[];
  order_index?: number;
  is_active?: boolean;
}

export interface Chapter {
  id: string;
  code: string;
  name: string;
  course_id: string;
  order_index?: number;
  description?: string;
  knowledge_points?: KnowledgePoint[];
}

export interface CourseCatalog {
  course_id: string;
  course_name: string;
  chapters: Chapter[];
}

export interface KnowledgeGraphNode {
  id: string;
  name: string;
  code: string;
  difficulty: number;
  tags?: string[];
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
  relation_type: string;
  strength?: number;
}

export interface KnowledgeGraph {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

export interface ExerciseContent {
  stem: string;
  options?: string[];
  image_url?: string;
}

export interface ExerciseHint {
  level: number;
  hint: string;
}

export interface Exercise {
  id: string;
  code: string;
  type: string;
  difficulty: number;
  content: ExerciseContent;
  answer: Record<string, any>;
  analysis?: string;
  hint_levels: ExerciseHint[];
  tags?: string[];
  knowledge_point_id: string;
  chapter_id: string;
  course_id: string;
}

export interface ExerciseBrief {
  id: string;
  code: string;
  type: string;
  difficulty: number;
  content: ExerciseContent;
  tags?: string[];
  hint_levels: ExerciseHint[];
}

export interface ExerciseRecommendation {
  exercises: ExerciseBrief[];
  recommendation_reason: string;
}
