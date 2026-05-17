export type GoalStatus = 'pending' | 'active' | 'completed' | 'cancelled';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type TaskType = 'learn' | 'practice' | 'review';

export interface LearnerGoal {
  id: string;
  title: string;
  description: string | null;
  course_id: string | null;
  status: GoalStatus;
  progress: number;
  target_date: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface LearnerGoalCreate {
  title: string;
  description?: string;
  course_id?: string;
  target_date?: string;
}

export interface LearnerGoalUpdate {
  title?: string;
  description?: string;
  target_date?: string;
  progress?: number;
}

export interface LearnerTask {
  id: string;
  title: string;
  description: string | null;
  goal_id: string | null;
  knowledge_point_id: string | null;
  exercise_id: string | null;
  type: TaskType;
  status: TaskStatus;
  priority: number;
  due_date: string | null;
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface LearnerTaskCreate {
  title: string;
  description?: string;
  goal_id?: string;
  knowledge_point_id?: string;
  exercise_id?: string;
  type?: TaskType;
  priority?: number;
  due_date?: string;
}
