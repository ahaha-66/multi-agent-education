import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { Course, CourseCatalog, KnowledgeGraph, Exercise } from '../types/course';
import { courseApi } from '../../services/courseApi';

interface CourseState {
  list: Course[];
  current: Course | null;
  catalog: CourseCatalog | null;
  knowledgeGraph: KnowledgeGraph | null;
  currentExercise: Exercise | null;
  loading: boolean;
  error: string | null;
}

const initialState: CourseState = {
  list: [],
  current: null,
  catalog: null,
  knowledgeGraph: null,
  currentExercise: null,
  loading: false,
  error: null,
};

export const fetchCourses = createAsyncThunk('course/fetchCourses', async () => {
  return await courseApi.getCourses();
});

export const fetchCourse = createAsyncThunk(
  'course/fetchCourse',
  async (courseId: string) => {
    return await courseApi.getCourse(courseId);
  }
);

export const fetchCourseCatalog = createAsyncThunk(
  'course/fetchCourseCatalog',
  async (courseId: string) => {
    return await courseApi.getCourseCatalog(courseId);
  }
);

export const fetchKnowledgeGraph = createAsyncThunk(
  'course/fetchKnowledgeGraph',
  async (courseId: string) => {
    return await courseApi.getKnowledgeGraph(courseId);
  }
);

const courseSlice = createSlice({
  name: 'course',
  initialState,
  reducers: {
    setCurrentCourse: (state, action: PayloadAction<Course>) => {
      state.current = action.payload;
    },
    setCurrentExercise: (state, action: PayloadAction<Exercise>) => {
      state.currentExercise = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCourses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourses.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch courses';
      })
      .addCase(fetchCourse.fulfilled, (state, action) => {
        state.current = action.payload;
      })
      .addCase(fetchCourseCatalog.fulfilled, (state, action) => {
        state.catalog = action.payload;
      })
      .addCase(fetchKnowledgeGraph.fulfilled, (state, action) => {
        state.knowledgeGraph = action.payload;
      });
  },
});

export const { setCurrentCourse, setCurrentExercise, clearError } = courseSlice.actions;
export default courseSlice.reducer;
