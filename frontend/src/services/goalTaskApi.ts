import api from './api';
import type {
  LearnerGoal,
  LearnerGoalCreate,
  LearnerGoalUpdate,
  LearnerTask,
  LearnerTaskCreate,
} from '../types/goal';

export const goalTaskApi = {
  getGoals: (learnerId: string, status?: string, courseId?: string) =>
    api.get<{ data: LearnerGoal[] }>(`/api/v1/learners/${learnerId}/goals`, {
      params: {
        status,
        course_id: courseId,
      },
    }),

  createGoal: (learnerId: string, data: LearnerGoalCreate) =>
    api.post<LearnerGoal>(`/api/v1/learners/${learnerId}/goals`, data),

  updateGoal: (learnerId: string, goalId: string, data: LearnerGoalUpdate) =>
    api.put<LearnerGoal>(`/api/v1/learners/${learnerId}/goals/${goalId}`, data),

  completeGoal: (learnerId: string, goalId: string) =>
    api.post<LearnerGoal>(`/api/v1/learners/${learnerId}/goals/${goalId}/complete`),

  getTasks: (learnerId: string, goalId?: string, status?: string) =>
    api.get<{ data: LearnerTask[] }>(`/api/v1/learners/${learnerId}/tasks`, {
      params: {
        goal_id: goalId,
        status,
      },
    }),

  createTask: (learnerId: string, data: LearnerTaskCreate) =>
    api.post<LearnerTask>(`/api/v1/learners/${learnerId}/tasks`, data),

  completeTask: (learnerId: string, taskId: string) =>
    api.post<LearnerTask>(`/api/v1/learners/${learnerId}/tasks/${taskId}/complete`),
};
