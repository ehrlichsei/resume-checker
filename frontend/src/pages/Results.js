import React, { useState, useEffect, useContext, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Button,
  Alert,
  MobileStepper,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { LangContext, languages } from '../contexts/LanguageContext';
import SwipeableViews from 'react-swipeable-views';
import api from '../api';

const Results = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { lang } = useContext(LangContext);
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [analysisMarkdown, setAnalysisMarkdown] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    const fetchResume = async () => {
      try {
        const response = await api.get(`/api/resumes/${slug}`);
        setResume(response.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    fetchResume();
  }, [slug]);

  useEffect(() => {
    if (!resume || !resume.processed || analysisMarkdown) return;

    // Only call analyze once when resume is processed and we haven't fetched markdown yet
    const fetchAnalysis = async () => {
      setIsAnalyzing(true);
      try {
        const res = await api.post(`/api/resumes/${slug}/analyze`);
        setAnalysisMarkdown(res.data.analysis_markdown);
      } catch (err) {
        setError('Failed to analyze resume');
      } finally {
        setIsAnalyzing(false);
      }
    };

    fetchAnalysis();
  }, [resume, slug, analysisMarkdown]);

  // Poll until the resume record is marked processed, then stop.
  useEffect(() => {
    if (!resume || resume.processed) return;

    const timer = setInterval(async () => {
      try {
        const res = await api.get(`/api/resumes/${slug}`);
        setResume(res.data);
        if (res.data.processed) {
          clearInterval(timer);
        }
      } catch (_) {}
    }, 3000);

    return () => clearInterval(timer);
  }, [resume, slug]);

  const sections = useMemo(() => {
    if (!analysisMarkdown) return [];
    // Split by numbered headings like "1." "2." etc.
    const parts = analysisMarkdown.split(/\n(?=\d+\.)/).filter(Boolean);
    return parts;
  }, [analysisMarkdown]);

  const [activeStep, setActiveStep] = useState(0);
  const maxSteps = sections.length;
  const [sending, setSending] = useState(false);

  const handleNext = () => {
    setActiveStep((prev) => Math.min(prev + 1, maxSteps - 1));
  };

  const handleBack = () => {
    setActiveStep((prev) => Math.max(prev - 1, 0));
  };

  const handleSendPdf = async () => {
    setSending(true);
    try {
      await api.post(`/api/resumes/${slug}/send-pdf`);
      alert(lang === languages.en ? 'Email sent!' : '邮件已发送！');
    } catch (e) {
      alert(e.response?.data?.error || 'Failed');
    } finally {
      setSending(false);
    }
  };

  if (loading || isAnalyzing || !analysisMarkdown) {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4, gap: 2 }}>
          <LinearProgress sx={{ width: '100%' }} />
          <Typography variant="body1">
            {isAnalyzing
              ? lang === languages.en
                ? 'Analyzing your resume. This may take up to a minute…'
                : '正在分析您的简历，可能需要一分钟…'
              : lang === languages.en
              ? 'Loading...'
              : '加载中…'}
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Alert severity="error" sx={{ my: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          {lang === languages.en ? 'Resume Analysis Results' : '简历分析结果'}
        </Typography>

        {sections.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <SwipeableViews index={activeStep} onChangeIndex={setActiveStep} enableMouseEvents>
              {sections.map((sec, idx) => (
                <Box key={idx} sx={{ p: 1 }}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ node, ...props }) => (
                        <Typography
                          variant="h5"
                          sx={{ fontWeight: 'bold', color: 'primary.main', mt: 3, mb: 1 }}
                          {...props}
                        />
                      ),
                      h2: ({ node, ...props }) => (
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 2, mb: 1 }} {...props} />
                      ),
                      li: ({ node, children, ...props }) => (
                        <Box
                          component="li"
                          sx={{ display: 'flex', alignItems: 'flex-start', mb: 0.5 }}
                          {...props}
                        >
                          <CheckCircleIcon fontSize="small" color="success" sx={{ mr: 1, mt: '2px' }} />
                          <Typography variant="body2" component="span">
                            {children}
                          </Typography>
                        </Box>
                      ),
                      p: ({ node, children }) => {
                        let text = '';
                        if (Array.isArray(children)) {
                          text = children.map((c) => (typeof c === 'string' ? c : '')).join('');
                        } else if (typeof children === 'string') {
                          text = children;
                        }
                        if (text.startsWith('关键词') || text.startsWith('Keywords')) {
                          const parts = text.split(':')[1]?.split(',').map((t) => t.trim()).filter(Boolean) || [];
                          return (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', mb: 2 }}>
                              {parts.map((tag, idx) => (
                                <Chip
                                  key={idx}
                                  label={tag}
                                  size="small"
                                  color="primary"
                                  sx={{ mr: 1, mb: 1 }}
                                />
                              ))}
                            </Box>
                          );
                        }
                        return (
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            {children}
                          </Typography>
                        );
                      },
                    }}
                  >
                    {sec}
                  </ReactMarkdown>
                </Box>
              ))}
            </SwipeableViews>
            {maxSteps > 1 && (
              <MobileStepper
                variant="dots"
                steps={maxSteps}
                position="static"
                activeStep={activeStep}
                nextButton={
                  <Button size="small" onClick={handleNext} disabled={activeStep === maxSteps - 1}>
                    {lang === languages.en ? 'Next' : '下一段'}
                  </Button>
                }
                backButton={
                  <Button size="small" onClick={handleBack} disabled={activeStep === 0}>
                    {lang === languages.en ? 'Back' : '上一段'}
                  </Button>
                }
              />
            )}
          </Box>
        )}

        <Box sx={{ mb: 4 }}>
          <Typography variant="h6">
            {lang === languages.en ? 'Basic Information' : '基本信息'}
          </Typography>
          <Typography>
            {lang === languages.en ? 'Email' : '邮箱'}: {resume.user_email}
          </Typography>
          <Typography>
            {lang === languages.en ? 'Resume File' : '文件名'}: {resume.filename}
          </Typography>
        </Box>

        <Grid container spacing={4}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6">
                {lang === languages.en ? 'Next Steps' : '下一步'}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  onClick={() => navigate(`/questionnaire/${slug}`)}
                  sx={{ mb: 2 }}
                >
                  {lang === languages.en ? 'Complete Questionnaire' : '填写问卷'}
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={handleSendPdf}
                  disabled={sending}
                >
                  {sending
                    ? lang === languages.en
                      ? 'Sending...'
                      : '发送中...'
                    : lang === languages.en
                    ? 'Email PDF'
                    : '发送 PDF 到邮箱'}
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default Results;
