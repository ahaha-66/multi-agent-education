import api from './api';
import type {
  PaginatedMistakes,
  MistakeRecordDetail,
  MistakeStatistics,
} from '../types/mistake';

export const mistakeApi = {
  getMistakes: (
    learnerId: string,
    params?: {
      courseId?: string;
      chapterId?: string;
      knowledgePointId?: string;
      isResolved?: boolean;
      page?: number;
      pageSize?: number;
    }
  ) =>
    api.get<PaginatedMistakes>(`/api/v1/learners/${learnerId}/mistakes`, {
      params: {
        course_id: params?.courseId,
        chapter_id: params?.chapterId,
        knowledge_point_id: params?.knowledgePointId,
        is_resolved: params?.isResolved,
        page: params?.page || 1,
        page_size: params?.pageSize || 20,
      },
    }),

  getMistake: (learnerId: string, mistakeId: string) =>
    api.get<MistakeRecordDetail>(`/api/v1/learners/${learnerId}/mistakes/${mistakeId}`),

  resolveMistake: (learnerId: string, mistakeId: string) =>
    api.post<MistakeRecordDetail>(`/api/v1/learners/${learnerId}/mistakes/${mistakeId}/resolve`),

  getStatistics: (learnerId: string) =>
    api.get<MistakeStatistics>(`/api/v1/learners/${learnerId}/mistakes/statistics`),
};
