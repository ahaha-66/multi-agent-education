import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type {
  LearnerGoal,
  LearnerGoalCreate,
  LearnerGoalUpdate,
  LearnerTask,
  LearnerTaskCreate,
} from '../types/goal';
import { goalTaskApi } from '../../services/goalTaskApi';

interface GoalState {
  goals: LearnerGoal[];
  tasks: LearnerTask[];
  activeGoal: LearnerGoal | null;
  loading: boolean;
  error: string | null;
}

const initialState: GoalState = {
  goals: [],
  tasks: [],
  activeGoal: null,
  loading: false,
  error: null,
};

export const fetchGoals = createAsyncThunk(
  'goal/fetchGoals',
  async ({
    learnerId,
    status,
    courseId,
  }: {
    learnerId: string;
    status?: string;
    courseId?: string;
  }) => {
    const response = await goalTaskApi.getGoals(learnerId, status, courseId);
    return response.data;
  }
);

export const createGoal = createAsyncThunk(
  'goal/createGoal',
  async ({
    learnerId,
    data,
  }: {
    learnerId: string;
    data: LearnerGoalCreate;
  }) => {
    return await goalTaskApi.createGoal(learnerId, data);
  }
);

export const updateGoal = createAsyncThunk(
  'goal/updateGoal',
  async ({
    learnerId,
    goalId,
    data,
  }: {
    learnerId: string;
    goalId: string;
    data: LearnerGoalUpdate;
  }) => {
    return await goalTaskApi.updateGoal(learnerId, goalId, data);
  }
);

export const completeGoal = createAsyncThunk(
  'goal/completeGoal',
  async ({ learnerId, goalId }: { learnerId: string; goalId: string }) => {
    return await goalTaskApi.completeGoal(learnerId, goalId);
  }
);

export const fetchTasks = createAsyncThunk(
  'goal/fetchTasks',
  async ({
    learnerId,
    goalId,
    status,
  }: {
    learnerId: string;
    goalId?: string;
    status?: string;
  }) => {
    const response = await goalTaskApi.getTasks(learnerId, goalId, status);
    return response.data;
  }
);

export const createTask = createAsyncThunk(
  'goal/createTask',
  async ({
    learnerId,
    data,
  }: {
    learnerId: string;
    data: LearnerTaskCreate;
  }) => {
    return await goalTaskApi.createTask(learnerId, data);
  }
);

export const completeTask = createAsyncThunk(
  'goal/completeTask',
  async ({ learnerId, taskId }: { learnerId: string; taskId: string }) => {
    return await goalTaskApi.completeTask(learnerId, taskId);
  }
);

const goalSlice = createSlice({
  name: 'goal',
  initialState,
  reducers: {
    setActiveGoal: (state, action: PayloadAction<LearnerGoal>) => {
      state.activeGoal = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchGoals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGoals.fulfilled, (state, action) => {
        state.loading = false;
        state.goals = action.payload;
      })
      .addCase(fetchGoals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch goals';
      })
      .addCase(createGoal.fulfilled, (state, action) => {
        state.goals.push(action.payload);
      })
      .addCase(updateGoal.fulfilled, (state, action) => {
        const index = state.goals.findIndex((g) => g.id === action.payload.id);
        if (index >= 0) {
          state.goals[index] = action.payload;
        }
        if (state.activeGoal?.id === action.payload.id) {
          state.activeGoal = action.payload;
        }
      })
      .addCase(completeGoal.fulfilled, (state, action) => {
        const index = state.goals.findIndex((g) => g.id === action.payload.id);
        if (index >= 0) {
          state.goals[index] = action.payload;
        }
        if (state.activeGoal?.id === action.payload.id) {
          state.activeGoal = action.payload;
        }
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.tasks = action.payload;
      })
      .addCase(createTask.fulfilled, (state, action) => {
        state.tasks.push(action.payload);
      })
      .addCase(completeTask.fulfilled, (state, action) => {
        const index = state.tasks.findIndex((t) => t.id === action.payload.id);
        if (index >= 0) {
          state.tasks[index] = action.payload;
        }
      });
  },
});

export const { setActiveGoal, clearError } = goalSlice.actions;
export default goalSlice.reducer;
