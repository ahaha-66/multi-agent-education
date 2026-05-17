export interface MistakeRecord {
  id: string;
  exercise_id: string;
  exercise_code: string;
  knowledge_point_id: string;
  knowledge_point_name: string;
  wrong_count: number;
  first_wrong_at: string;
  last_wrong_at: string;
  is_resolved: boolean;
}

export interface MistakeRecordDetail extends MistakeRecord {
  content: Record<string, any>;
  correct_answer: any;
  last_attempt_answer: any;
  analysis?: string;
}

export interface MistakeStatistics {
  total_mistakes: number;
  resolved_mistakes: number;
  unresolved_mistakes: number;
  by_knowledge_point: {
    knowledge_point_id: string;
    knowledge_point_name: string;
    count: number;
  }[];
}

export interface PaginatedMistakes {
  mistakes: MistakeRecord[];
  total: number;
  page: number;
  page_size: number;
}
