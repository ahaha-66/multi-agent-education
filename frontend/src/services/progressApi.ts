import api from './api';
import type { OverallProgress, CourseProgress } from '../types/progress';

export const progressApi = {
  getOverallProgress: (learnerId: string) => api.get<OverallProgress>(`/api/v1/learners/${learnerId}/progress`),

  getCourseProgress: (learnerId: string, courseId: string) =>
    api.get<CourseProgress>(`/api/v1/learners/${learnerId}/progress/courses/${courseId}`),
};
