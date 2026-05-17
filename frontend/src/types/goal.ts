export interface LearnerGoalexport interface LearnerGoal {export interface LearnerGoal {
  id: string;
  learner_id: string;
  title: string;
export interface LearnerGoal {
  id: string;
  learner_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'active' | 'completed';export interface LearnerGoal {
  id: string;
  learner_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'active' | 'completed';
  progress: number;
  target_date?: string;
  created_at: string;export interface LearnerGoal {
  id: string;
  learner_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'active' | 'completed';
  progress: number;
  target_date?: string;
  created_at: string;
  updated_at: string;
}

export interface LearnerGoalCreate {
  titleexport interface LearnerGoal {
  id: string;
  learner_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'active' | 'completed';
  progress: number;
  target_date?: string;
  created_at: string;
  updated_at: string;
}

export interface LearnerGoalCreate {
  title: string;
  description?: string;
  target_date?: string;
}

exportexport interface LearnerGoal {
  id: string;
  learner_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'active' | 'completed';
  progress: number;
  target_date?: string;
  created_at: string;
  updated_at: string;
}

export interface LearnerGoalCreate {
  title: string;
  description?: string;
  target_date?: string;
}

export interface LearnerGoalUpdate {
  title?: string;
  description?: string;
  target_date?: string;
}

exportexport interface LearnerGoal {
  id: string;
  learner_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'active' | 'completed';
  progress: number;
  target_date?: string;
  created_at: string;
  updated_at: string;
}

export interface LearnerGoalCreate {
  title: string;
  description?: string;
  target_date?: string;
}

export interface LearnerGoalUpdate {
  title?: string;
  description?: string;
  target_date?: string;
}

export interface LearnerTask {
  id: string;