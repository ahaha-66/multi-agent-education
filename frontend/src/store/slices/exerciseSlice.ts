import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type {
  Exercise,
  AnswerVerificationRequest,
  AnswerVerificationResponse,
} from '../types/exercise';
import { courseApi } from '../services/courseApi';

interface ExerciseState {
  current: Exercise | null;
  answer: any;
  feedback: AnswerVerificationResponse | null;
  isSubmitting: boolean;
  hintLevel: number;
  error: string | null;
}

const initialState: ExerciseState = {
  current: null,
  answer: null,
  feedback: null,
  isSubmitting: false,
  hintLevel: 0,
  error: null,
};

export const fetchNextExercise = createAsyncThunk(
  'exercise/fetchNext',
  async ({
    courseId,
    learnerId,
    knowledgePointId,
  }: {
    courseId: string;
    learnerId: string;
    knowledgePointId?: string;
  }) => {
    const response = await courseApi.getNextExercise(courseId, learnerId, knowledgePointId);
    return response.exercises[0];
  }
);

export const submitAnswer = createAsyncThunk(
  'exercise/submitAnswer',
  async ({
    request,
    learnerId,
  }: {
    request: AnswerVerificationRequest;
    learnerId?: string;
  }) => {
    return await courseApi.verifyAnswer(request, learnerId);
  }
);

const exerciseSlice = createSlice({
  name: 'exercise',
  initialState,
  reducers: {
    setAnswer: (state, action: PayloadAction<any>) => {
      state.answer = action.payload;
    },
    clearAnswer: (state) => {
      state.answer = null;
      state.feedback = null;
      state.hintLevel = 0;
    },
    incrementHintLevel: (state) => {
      if (state.hintLevel < 3) {
        state.hintLevel += 1;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNextExercise.pending, (state) => {
        state.error = null;
      })
      .addCase(fetchNextExercise.fulfilled, (state, action) => {
        state.current = action.payload;
        state.answer = null;
        state.feedback = null;
        state.hintLevel = 0;
      })
      .addCase(fetchNextExercise.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch exercise';
      })
      .addCase(submitAnswer.pending, (state) => {
        state.isSubmitting = true;
        state.error = null;
      })
      .addCase(submitAnswer.fulfilled, (state, action) => {
        state.isSubmitting = false;
        state.feedback = action.payload;
      })
      .addCase(submitAnswer.rejected, (state, action) => {
        state.isSubmitting = false;
        state.error = action.error.message || 'Failed to submit answer';
      });
  },
});

export const { setAnswer, clearAnswer, incrementHintLevel, clearError } =
  exerciseSlice.actions;
export default exerciseSlice.reducer;
