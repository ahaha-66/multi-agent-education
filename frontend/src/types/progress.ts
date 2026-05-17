export interface ChapterProgress {
  chapter_id: string;
  chapter_name: string;
  progress: number;
  completed_knowledge_points: number;
  total_knowledge_points: number;
}

export interface CourseProgress {
  course_id: string;
  course_name: string;
  overall_progress: number;
  completed_chapters: number;
  total_chapters: number;
  mastered_knowledge_points: number;
  total_knowledge_points: number;
  chapters: ChapterProgress[];
}

export interface OverallProgress {
  learner_id: string;
  overall_progress: number;
  total_courses: number;
  completed_courses: number;
  courses: CourseProgress[];
}
