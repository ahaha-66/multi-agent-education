import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { userApi } from '../../services/userApi';

interface UserProfile {
  id: string;
  name: string;
  avatar?: string;
  email?: string;
  grade?: number;
  school?: string;
  createdAt: string;
  lastActiveAt: string;
  totalStudyDays: number;
  totalPoints: number;
  streak: number;
}

interface UserSettings {
  theme: 'light' | 'dark' | 'auto';
  language: 'zh' | 'en';
  notifications: {
    email: boolean;
    push: boolean;
    reminder: boolean;
  };
  practice: {
    difficulty: 'easy' | 'medium' | 'hard';
    autoPlayHints: boolean;
    showAnswerImmediately: boolean;
  };
  display: {
    showProgress: boolean;
    compactMode: boolean;
  };
}

interface UserState {
  id: string;
  profile: UserProfile | null;
  settings: UserSettings;
  currentCourseId: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const defaultSettings: UserSettings = {
  theme: 'light',
  language: 'zh',
  notifications: {
    email: true,
    push: true,
    reminder: true,
  },
  practice: {
    difficulty: 'medium',
    autoPlayHints: false,
    showAnswerImmediately: false,
  },
  display: {
    showProgress: true,
    compactMode: false,
  },
};

const initialState: UserState = {
  id: import.meta.env.VITE_LEARNER_ID || 'learner_001',
  profile: null,
  settings: defaultSettings,
  currentCourseId: null,
  isAuthenticated: true,
  loading: false,
  error: null,
};

export const fetchUserProfile = createAsyncThunk(
  'user/fetchProfile',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await userApi.getProfile(userId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || '获取用户信息失败');
    }
  }
);

export const updateUserProfile = createAsyncThunk(
  'user/updateProfile',
  async ({ userId, data }: { userId: string; data: Partial<UserProfile> }, { rejectWithValue }) => {
    try {
      const response = await userApi.updateProfile(userId, data);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || '更新用户信息失败');
    }
  }
);

export const updateUserSettings = createAsyncThunk(
  'user/updateSettings',
  async ({ userId, settings }: { userId: string; settings: Partial<UserSettings> }, { rejectWithValue }) => {
    try {
      const response = await userApi.updateSettings(userId, settings);
      return settings;
    } catch (error: any) {
      return rejectWithValue(error.message || '更新设置失败');
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setCurrentCourse: (state, action: PayloadAction<string | null>) => {
      state.currentCourseId = action.payload;
    },
    updateSettingsLocal: (state, action: PayloadAction<Partial<UserSettings>>) => {
      state.settings = { ...state.settings, ...action.payload };
    },
    setUserProfile: (state, action: PayloadAction<UserProfile>) => {
      state.profile = action.payload;
      state.isAuthenticated = true;
    },
    clearUserError: (state) => {
      state.error = null;
    },
    logout: (state) => {
      state.profile = null;
      state.isAuthenticated = false;
      state.currentCourseId = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(updateUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = { ...state.profile, ...action.payload } as UserProfile;
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(updateUserSettings.fulfilled, (state, action) => {
        state.settings = { ...state.settings, ...action.payload };
      });
  },
});

export const { 
  setCurrentCourse, 
  updateSettingsLocal, 
  setUserProfile, 
  clearUserError,
  logout 
} = userSlice.actions;

export default userSlice.reducer;
