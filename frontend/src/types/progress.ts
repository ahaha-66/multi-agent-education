export interface KnowledgePointProgress {
  knowledge_point_id: string;
  code: string;
  name: string;
  mastery: number;
  is_mastered: boolean;
  attempts: number;
  correct_count: number;
  wrong_streak: number;
  last_attempt_at: string | null;
}

export interface ChapterProgress {
  chapter_id: string;
  chapter_name: string;
  progress: number;
  knowledge_points: KnowledgePointProgress[];
}

export interface CourseProgress {
  course_id: string;
  course_name: string;
  overall_progress: number;
  total_chapters: number;
  completed_chapters: number;
  total_knowledge_points: number;
  mastered_knowledge_points: number;
  chapters: ChapterProgress[];
}

export interface OverallProgress {
  learner_id: string;
  total_courses: number;
  completed_courses: number;
  courses: CourseProgress[];
}
