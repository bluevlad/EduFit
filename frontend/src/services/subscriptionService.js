import apiClient from './apiClient';

export const requestSubscription = (email) =>
  apiClient.post('/subscriptions/request', { email });

export const verifySubscription = (email, code) =>
  apiClient.post('/subscriptions/verify', { email, code });
