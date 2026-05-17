import api from './api';
import type { Course, CourseCatalog, KnowledgeGraph, ExerciseRecommendation } from '../types/course';
import type { AnswerVerificationRequest, AnswerVerificationResponse } from '../types/exercise';

export const courseApi = {
  getCourses: () => api.get<Course[]>('/api/v1/courses'),

  getCourse: (courseId: string) => api.get<Course>(`/api/v1/courses/${courseId}`),

  getCourseCatalog: (courseId: string) => api.get<CourseCatalog>(`/api/v1/courses/${courseId}/catalog`),

  getKnowledgeGraph: (courseId: string) => api.get<KnowledgeGraph>(`/api/v1/courses/${courseId}/knowledge-graph`),

  getNextExercise: (courseId: string, learnerId: string, knowledgePointId?: string, count?: number) =>
    api.get<ExerciseRecommendation>(`/api/v1/courses/${courseId}/exercises/next`, {
      params: {
        learner_id: learnerId,
        knowledge_point_id: knowledgePointId,
        count: count || 1,
      },
    }),

  verifyAnswer: (data: AnswerVerificationRequest, learnerId?: string) =>
    api.post<AnswerVerificationResponse>('/api/v1/exercises/verify', data, {
      params: learnerId ? { learner_id: learnerId } : undefined,
    }),
};
