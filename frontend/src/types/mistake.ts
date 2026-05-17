export interface MistakeRecord {
  id: string;
  exercise_id: string;
  exercise_code: string;
  exercise_type: string;
  knowledge_point_id: string;
  knowledge_point_name: string;
  first_wrong_at: string;
  last_wrong_at: string;
  wrong_count: number;
  is_resolved: boolean;
}

export interface MistakeRecordDetail extends MistakeRecord {
  content: any;
  correct_answer: any;
  analysis?: string;
  last_attempt_answer: any;
}

export interface MistakeStatistics {
  learner_id: string;
  total_mistakes: number;
  resolved_mistakes: number;
  unresolved_mistakes: number;
  by_knowledge_point: Array<{
    knowledge_point_id: string;
    knowledge_point_name: string;
    mistake_count: number;
  }>;
}

export interface PaginatedMistakes {
  learner_id: string;
  mistakes: MistakeRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
