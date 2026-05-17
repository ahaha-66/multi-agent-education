import api from './api';

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
  theme?: 'light' | 'dark' | 'auto';
  language?: 'zh' | 'en';
  notifications?: {
    email?: boolean;
    push?: boolean;
    reminder?: boolean;
  };
  practice?: {
    difficulty?: 'easy' | 'medium' | 'hard';
    autoPlayHints?: boolean;
    showAnswerImmediately?: boolean;
  };
  display?: {
    showProgress?: boolean;
    compactMode?: boolean;
  };
}

export const userApi = {
  getProfile: async (userId: string): Promise<UserProfile> => {
    try {
      const response = await api.get<UserProfile>(`/users/${userId}/profile`);
      return response.data;
    } catch (error) {
      const defaultProfile: UserProfile = {
        id: userId,
        name: '学习者',
        avatar: undefined,
        email: undefined,
        grade: undefined,
        school: undefined,
        createdAt: new Date().toISOString(),
        lastActiveAt: new Date().toISOString(),
        totalStudyDays: 1,
        totalPoints: 0,
        streak: 0,
      };
      return defaultProfile;
    }
  },

  updateProfile: async (
    userId: string,
    data: Partial<UserProfile>
  ): Promise<UserProfile> => {
    const response = await api.patch<UserProfile>(`/users/${userId}/profile`, data);
    return response.data;
  },

  getSettings: async (userId: string): Promise<UserSettings> => {
    const response = await api.get<UserSettings>(`/users/${userId}/settings`);
    return response.data;
  },

  updateSettings: async (
    userId: string,
    settings: UserSettings
  ): Promise<UserSettings> => {
    const response = await api.patch<UserSettings>(`/users/${userId}/settings`, settings);
    return response.data;
  },

  getStatistics: async (userId: string) => {
    const response = await api.get(`/users/${userId}/statistics`);
    return response.data;
  },

  updateAvatar: async (userId: string, avatarUrl: string): Promise<void> => {
    await api.patch(`/users/${userId}/avatar`, { avatar: avatarUrl });
  },

  resetProgress: async (userId: string): Promise<void> => {
    await api.post(`/users/${userId}/reset-progress`);
  },
};
