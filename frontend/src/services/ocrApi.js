import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL });

export const uploadDocument = (formData) =>
  api.post("/api/v1/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const queryDocument = (doc_id, question) =>
  api.post("/api/v1/query", { doc_id, question });

export const getDocument = (doc_id) =>
  api.get(`/api/v1/document/${doc_id}`);
