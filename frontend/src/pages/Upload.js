import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Paper,
  TextField,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import api from '../api';
import { LangContext, languages } from '../contexts/LanguageContext';

const Upload = () => {
  const navigate = useNavigate();
  const { lang } = useContext(LangContext);

  const t = {
    title: lang === languages.en ? 'Upload Your Resume' : '上传您的简历',
    emailLabel: lang === languages.en ? 'Email' : '邮箱 *',
    chooseFile: lang === languages.en ? 'Choose PDF File' : '选择 PDF 文件',
    uploadSuccess: lang === languages.en ? 'Resume uploaded successfully.' : '简历上传成功。',
    analyzeBtn: lang === languages.en ? 'Analyze Resume' : '分析简历',
    fillAllFields: lang === languages.en ? 'Please fill in all fields' : '请填写所有字段',
    analysisFailed: lang === languages.en ? 'Analysis failed' : '分析失败',
    dragPrompt: lang === languages.en ? 'Drag and drop PDF here' : '将 PDF 拖拽到此处',
    orClick: lang === languages.en ? 'or click to select' : '或点击选择',
    dropPdfOnly: lang === languages.en ? 'Please drop a PDF file' : '请拖拽 PDF 文件',
  };

  const [email, setEmail] = useState('');
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const handleProcess = async () => {
    setError('');

    if (!email || !file) {
      setError(t.fillAllFields);
      return;
    }

    setProcessing(true);
    try {
      // 1) upload
      const formData = new FormData();
      formData.append('email', email);
      formData.append('resume', file);

      const uploadRes = await api.post('/api/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const slug = uploadRes.data.resume_slug;

      // save JWT token for subsequent requests
      if (uploadRes.data.token) {
        localStorage.setItem('jwt', uploadRes.data.token);
      }

      // 2) analyze
      await api.post(`/api/resumes/${slug}/analyze`);

      // 3) navigate to results
      navigate(`/results/${slug}`);
    } catch (err) {
      setError(err.response?.data?.message || t.analysisFailed);
    } finally {
      setProcessing(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const dropped = e.dataTransfer.files[0];
      if (dropped.type === 'application/pdf') {
        setFile(dropped);
      } else {
        setError(t.dropPdfOnly);
      }
      e.dataTransfer.clearData();
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          {t.title}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={(e) => { e.preventDefault(); handleProcess(); }}>
          <TextField
            fullWidth
            label={t.emailLabel}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            margin="normal"
            required
          />

          <Box sx={{ mt: 2 }}>
            <input
              accept="application/pdf"
              style={{ display: 'none' }}
              id="resume-upload"
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <Box
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('resume-upload').click()}
              sx={{
                border: '2px dashed',
                borderColor: dragOver ? 'primary.main' : 'grey.400',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
              }}
            >
              <Typography>{file ? file.name : t.dragPrompt}</Typography>
              {!file && (
                <Typography variant="caption" color="text.secondary">
                  {t.orClick}
                </Typography>
              )}
            </Box>
          </Box>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 3, mb: 2 }}
            disabled={processing}
          >
            {processing ? <CircularProgress size={24} /> : t.analyzeBtn}
          </Button>
        </form>
      </Paper>
    </Container>
  );
};

export default Upload;
