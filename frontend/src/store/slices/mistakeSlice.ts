import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type {
  PaginatedMistakes,
  MistakeRecordDetail,
  MistakeStatistics,
} from '../types/mistake';
import { mistakeApi } from '../services/mistakeApi';

interface MistakeState {
  list: PaginatedMistakes | null;
  detail: MistakeRecordDetail | null;
  statistics: MistakeStatistics | null;
  filters: {
    courseId: string | null;
    chapterId: string | null;
    knowledgePointId: string | null;
    isResolved: boolean | null;
  };
  loading: boolean;
  error: string | null;
}

const initialState: MistakeState = {
  list: null,
  detail: null,
  statistics: null,
  filters: {
    courseId: null,
    chapterId: null,
    knowledgePointId: null,
    isResolved: null,
  },
  loading: false,
  error: null,
};

export const fetchMistakes = createAsyncThunk(
  'mistake/fetchMistakes',
  async ({
    learnerId,
    params,
  }: {
    learnerId: string;
    params?: any;
  }) => {
    return await mistakeApi.getMistakes(learnerId, params);
  }
);

export const fetchMistakeDetail = createAsyncThunk(
  'mistake/fetchDetail',
  async ({ learnerId, mistakeId }: { learnerId: string; mistakeId: string }) => {
    return await mistakeApi.getMistake(learnerId, mistakeId);
  }
);

export const resolveMistake = createAsyncThunk(
  'mistake/resolveMistake',
  async ({ learnerId, mistakeId }: { learnerId: string; mistakeId: string }) => {
    return await mistakeApi.resolveMistake(learnerId, mistakeId);
  }
);

export const fetchMistakeStatistics = createAsyncThunk(
  'mistake/fetchStatistics',
  async (learnerId: string) => {
    return await mistakeApi.getStatistics(learnerId);
  }
);

const mistakeSlice = createSlice({
  name: 'mistake',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<MistakeState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMistakes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMistakes.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchMistakes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch mistakes';
      })
      .addCase(fetchMistakeDetail.fulfilled, (state, action) => {
        state.detail = action.payload;
      })
      .addCase(resolveMistake.fulfilled, (state, action) => {
        state.detail = action.payload;
        if (state.list) {
          const index = state.list.mistakes.findIndex(
            (m) => m.id === action.payload.id
          );
          if (index >= 0) {
            state.list.mistakes[index] = action.payload;
          }
        }
      })
      .addCase(fetchMistakeStatistics.fulfilled, (state, action) => {
        state.statistics = action.payload;
      });
  },
});

export const { setFilters, clearError } = mistakeSlice.actions;
export default mistakeSlice.reducer;
