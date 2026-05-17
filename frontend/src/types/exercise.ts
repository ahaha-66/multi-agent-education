export type ExerciseType = 'single_choice' | 'multiple_choice' | 'true_false' | 'fill_blank';

export interface ExerciseContent {
  stem: string;
  options?: string[];
}

export interface HintLevel {
  level: number;
  hint: string;
}

export interface Exercise {
  id: string;
  code: string;
  type: ExerciseType;
  difficulty: number;
  content: ExerciseContent;
  answer: any;
  analysis?: string;
  tags: string[];
  hint_levels: HintLevel[];
}

export interface ExerciseRecommendation {
  exercises: Exercise[];
  recommendation_reason: string;
}

export interface AnswerVerificationRequest {
  exercise_id: string;
  answer: any;
}

export interface AnswerVerificationResponse {
  exercise_id: string;
  is_correct: boolean;
  correct_answer: any;
  analysis?: string;
}
