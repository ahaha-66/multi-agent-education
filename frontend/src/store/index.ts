import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import userReducer from './slices/userSlice';
import courseReducer from './slices/courseSlice';
import exerciseReducer from './slices/exerciseSlice';
import progressReducer from './slices/progressSlice';
import mistakeReducer from './slices/mistakeSlice';
import goalReducer from './slices/goalSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    course: courseReducer,
    exercise: exerciseReducer,
    progress: progressReducer,
    mistake: mistakeReducer,
    goal: goalReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
