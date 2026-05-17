import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserState {
  id: string;
  currentCourseId: string | null;
  settings: Record<string, any>;
}

const initialState: UserState = {
  id: import.meta.env.VITE_LEARNER_ID || 'learner_001',
  currentCourseId: null,
  settings: {},
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setCurrentCourse: (state, action: PayloadAction<string>) => {
      state.currentCourseId = action.payload;
    },
    updateSettings: (state, action: PayloadAction<Partial<UserState['settings']>>) => {
      state.settings = { ...state.settings, ...action.payload };
    },
  },
});

export const { setCurrentCourse, updateSettings } = userSlice.actions;
export default userSlice.reducer;
