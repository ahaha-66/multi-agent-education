import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { OverallProgress, CourseProgress } from '../types/progress';
import { progressApi } from '../services/progressApi';

interface ProgressState {
  overall: OverallProgress | null;
  courses: CourseProgress[];
  loading: boolean;
  error: string | null;
}

const initialState: ProgressState = {
  overall: null,
  courses: [],
  loading: false,
  error: null,
};

export const fetchOverallProgress = createAsyncThunk(
  'progress/fetchOverall',
  async (learnerId: string) => {
    return await progressApi.getOverallProgress(learnerId);
  }
);

export const fetchCourseProgress = createAsyncThunk(
  'progress/fetchCourse',
  async ({ learnerId, courseId }: { learnerId: string; courseId: string }) => {
    return await progressApi.getCourseProgress(learnerId, courseId);
  }
);

const progressSlice = createSlice({
  name: 'progress',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOverallProgress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOverallProgress.fulfilled, (state, action) => {
        state.loading = false;
        state.overall = action.payload;
        state.courses = action.payload.courses;
      })
      .addCase(fetchOverallProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch progress';
      })
      .addCase(fetchCourseProgress.fulfilled, (state, action) => {
        const existingIndex = state.courses.findIndex(
          (c) => c.course_id === action.payload.course_id
        );
        if (existingIndex >= 0) {
          state.courses[existingIndex] = action.payload;
        } else {
          state.courses.push(action.payload);
        }
        if (state.overall) {
          const courseIndex = state.overall.courses.findIndex(
            (c) => c.course_id === action.payload.course_id
          );
          if (courseIndex >= 0) {
            state.overall.courses[courseIndex] = action.payload;
          }
        }
      });
  },
});

export const { clearError } = progressSlice.actions;
export default progressSlice.reducer;
