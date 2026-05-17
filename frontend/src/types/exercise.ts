import type { Exercise, ExerciseBrief } from './course';

export interface AnswerVerificationRequest {
  exercise_id: string;
  answer: any;
}

export interface AnswerVerificationResponse {
  is_correct: boolean;
  correct_answer: any;
  analysis?: string;
  mastery_change?: number;
}

export interface ExerciseRecommendation {
  exercises: ExerciseBrief[];
  recommendation_reason: string;
}

export type { Exercise, ExerciseBrief };
