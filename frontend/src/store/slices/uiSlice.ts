import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UiState {
  sidebarCollapsed: boolean;
  loading: boolean;
  notification: {
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
  } | null;
}

const initialState: UiState = {
  sidebarCollapsed: false,
  loading: false,
  notification: null,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    showNotification: (
      state,
      action: PayloadAction<{ type: UiState['notification']['type']; message: string }>
    ) => {
      state.notification = action.payload;
    },
    hideNotification: (state) => {
      state.notification = null;
    },
  },
});

export const { toggleSidebar, setSidebarCollapsed, setLoading, showNotification, hideNotification } = uiSlice.actions;
export default uiSlice.reducer;
