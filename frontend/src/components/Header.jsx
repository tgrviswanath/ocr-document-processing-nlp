import React from "react";
import { AppBar, Toolbar, Typography, Chip, Box } from "@mui/material";
import DocumentScannerIcon from "@mui/icons-material/DocumentScanner";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar sx={{ gap: 1 }}>
        <DocumentScannerIcon />
        <Typography variant="h6" fontWeight="bold">
          OCR Document Processing
        </Typography>
        <Box sx={{ ml: 2, display: "flex", gap: 1 }}>
          <Chip label="Tesseract" size="small" sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }} />
          <Chip label="spaCy NER" size="small" sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }} />
          <Chip label="FAISS + Ollama" size="small" sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }} />
        </Box>
      </Toolbar>
    </AppBar>
  );
}
