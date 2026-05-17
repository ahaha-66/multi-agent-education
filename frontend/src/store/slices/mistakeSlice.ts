import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { MistakeRecord, MistakeRecordDetail, MistakeStatistics, PaginatedMistakes } from '../types/mistake';
import { mistakeApi } from '../../services/mistakeApi';

interface MistakeState {
  list: PaginatedMistakes | null;
  detail: MistakeRecordDetail | null;
  statistics: MistakeStatistics | null;
  loading: boolean;
  error: string | null;
}

const initialState: MistakeState = {
  list: null,
  detail: null,
  statistics: null,
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
    params?: {
      isResolved?: boolean;
      page?: number;
      pageSize?: number;
    };
  }) => {
    return await mistakeApi.getMistakes(learnerId, params);
  }
);

export const fetchMistakeDetail = createAsyncThunk(
  'mistake/fetchDetail',
  async ({ learnerId, mistakeId }: { learnerId: string; mistakeId: string }) => {
    return await mistakeApi.getMistakeDetail(learnerId, mistakeId);
  }
);

export const resolveMistake = createAsyncThunk(
  'mistake/resolve',
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
        if (state.list?.mistakes) {
          const index = state.list.mistakes.findIndex((m) => m.id === action.payload.id);
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

export const { clearError } = mistakeSlice.actions;
export default mistakeSlice.reducer;
