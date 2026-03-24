import React, { useState, useRef } from "react";
import {
  Box, Button, CircularProgress, Alert, Typography, Paper,
  Chip, TextField, Divider, Tabs, Tab, Table, TableBody,
  TableCell, TableHead, TableRow, LinearProgress, Accordion,
  AccordionSummary, AccordionDetails, IconButton, Tooltip,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import SearchIcon from "@mui/icons-material/Search";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { uploadDocument, queryDocument } from "../services/ocrApi";

const ENTITY_COLORS = {
  PERSON: "primary", ORG: "secondary", GPE: "success",
  LOC: "success", DATE: "warning", MONEY: "error",
  PRODUCT: "info", LAW: "default", PERCENT: "default",
};

const SAMPLE_QUESTIONS = [
  "What is the main topic of this document?",
  "Who are the key people mentioned?",
  "What organizations are referenced?",
  "What dates are mentioned?",
  "What is the conclusion or summary?",
];

export default function OCRPage() {
  const [tab, setTab] = useState(0);
  const [docResult, setDocResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [question, setQuestion] = useState("");
  const [qaResult, setQaResult] = useState(null);
  const [querying, setQuerying] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    setError("");
    setDocResult(null);
    setQaResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await uploadDocument(fd);
      setDocResult(r.data);
      setTab(1); // jump to results tab
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async () => {
    if (!question.trim() || !docResult?.doc_id) return;
    setQuerying(true);
    setError("");
    setQaResult(null);
    try {
      const r = await queryDocument(docResult.doc_id, question);
      setQaResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Query failed.");
    } finally {
      setQuerying(false);
    }
  };

  // Group entities by label
  const entityGroups = docResult?.entities?.reduce((acc, e) => {
    acc[e.label] = acc[e.label] || [];
    acc[e.label].push(e.text);
    return acc;
  }, {}) || {};

  return (
    <Box>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="📤 Upload Document" />
        <Tab label="📊 Results & Entities" disabled={!docResult} />
        <Tab label="💬 Ask Questions" disabled={!docResult} />
      </Tabs>

      {/* ── Tab 0: Upload ── */}
      {tab === 0 && (
        <Paper
          variant="outlined"
          onClick={() => fileRef.current.click()}
          onDrop={(e) => { e.preventDefault(); handleUpload(e.dataTransfer.files[0]); }}
          onDragOver={(e) => e.preventDefault()}
          sx={{
            p: 6, textAlign: "center", cursor: "pointer", borderStyle: "dashed",
            "&:hover": { bgcolor: "action.hover" },
          }}
        >
          <input
            ref={fileRef} type="file" hidden
            accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif,.bmp,.webp"
            onChange={(e) => handleUpload(e.target.files[0])}
          />
          {uploading
            ? <Box>
                <CircularProgress size={36} sx={{ mb: 1 }} />
                <Typography color="text.secondary">Processing document…</Typography>
                <LinearProgress sx={{ mt: 2, maxWidth: 300, mx: "auto" }} />
              </Box>
            : <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 1 }}>
                <UploadFileIcon color="action" sx={{ fontSize: 48 }} />
                <Typography variant="h6">Drag & drop or click to upload</Typography>
                <Typography variant="body2" color="text.secondary">
                  PDF, PNG, JPG, TIFF, BMP, WEBP
                </Typography>
              </Box>
          }
        </Paper>
      )}

      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

      {/* ── Tab 1: Results & Entities ── */}
      {tab === 1 && docResult && (
        <Box>
          {/* Stats row */}
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mb: 3 }}>
            {[
              { label: "Pages", value: docResult.pages },
              { label: "Words", value: docResult.word_count.toLocaleString() },
              { label: "Characters", value: docResult.char_count.toLocaleString() },
              { label: "OCR Engine", value: docResult.source },
              { label: "Entities Found", value: docResult.entities.length },
            ].map((s) => (
              <Paper key={s.label} variant="outlined" sx={{ p: 2, minWidth: 110, textAlign: "center" }}>
                <Typography variant="h6" fontWeight="bold">{s.value}</Typography>
                <Typography variant="caption" color="text.secondary">{s.label}</Typography>
              </Paper>
            ))}
          </Box>

          {/* Entities by group */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Named Entities ({docResult.entities.length})
          </Typography>
          {Object.keys(entityGroups).length === 0
            ? <Alert severity="info" sx={{ mb: 2 }}>No entities detected.</Alert>
            : (
              <Paper variant="outlined" sx={{ mb: 3 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ bgcolor: "grey.50" }}>
                      <TableCell>Type</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Entities</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(entityGroups).map(([label, items]) => (
                      <TableRow key={label} hover>
                        <TableCell>
                          <Chip
                            label={label}
                            size="small"
                            color={ENTITY_COLORS[label] || "default"}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {docResult.entities.find((e) => e.label === label)?.description}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                            {[...new Set(items)].slice(0, 8).map((item, i) => (
                              <Chip key={i} label={item} size="small" variant="outlined" />
                            ))}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Paper>
            )
          }

          {/* Extracted text preview */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">Extracted Text Preview</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 1 }}>
                <Tooltip title="Copy text">
                  <IconButton size="small" onClick={() => navigator.clipboard.writeText(docResult.text_preview)}>
                    <ContentCopyIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography
                variant="body2"
                component="pre"
                sx={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: "0.8rem" }}
              >
                {docResult.text_preview}
                {docResult.char_count > 500 && "\n\n… (truncated)"}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Button
            variant="contained" sx={{ mt: 2 }}
            onClick={() => setTab(2)}
          >
            Ask Questions About This Document →
          </Button>
        </Box>
      )}

      {/* ── Tab 2: Q&A ── */}
      {tab === 2 && docResult && (
        <Box>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Document: <strong>{docResult.filename}</strong> · {docResult.word_count} words
          </Typography>

          {/* Sample questions */}
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
            {SAMPLE_QUESTIONS.map((q, i) => (
              <Chip
                key={i} label={q} size="small" variant="outlined"
                onClick={() => setQuestion(q)} clickable
              />
            ))}
          </Box>

          <TextField
            fullWidth multiline rows={2}
            label="Ask a question about the document"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained" size="large" fullWidth
            disabled={!question.trim() || querying}
            onClick={handleQuery}
            startIcon={querying ? <CircularProgress size={18} color="inherit" /> : <SearchIcon />}
          >
            {querying ? "Searching…" : "Ask"}
          </Button>

          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

          {qaResult && (
            <Paper elevation={2} sx={{ mt: 3, p: 3, borderLeft: 4, borderColor: "primary.main" }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Answer</Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>{qaResult.answer}</Typography>

              <Divider sx={{ mb: 2 }} />

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Source Chunks ({qaResult.source_chunks.length})
              </Typography>
              {qaResult.source_chunks.map((c, i) => (
                <Paper key={i} variant="outlined" sx={{ p: 1.5, mb: 1 }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">Chunk {i + 1}</Typography>
                    <Chip label={`Score: ${c.score}`} size="small" color="primary" variant="outlined" />
                  </Box>
                  <Typography variant="body2" sx={{ fontStyle: "italic" }}>
                    "{c.chunk.slice(0, 200)}{c.chunk.length > 200 ? "…" : ""}"
                  </Typography>
                </Paper>
              ))}
            </Paper>
          )}
        </Box>
      )}
    </Box>
  );
}
