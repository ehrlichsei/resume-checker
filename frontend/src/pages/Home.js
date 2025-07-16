import React, { useContext } from 'react';
import { Box, Container, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { LangContext, languages } from '../contexts/LanguageContext';

const Home = () => {
  const navigate = useNavigate();
  const { lang } = useContext(LangContext);

  const t = {
    title: lang === languages.en ? 'Resume Optimizer' : '简历优化器',
    subtitle: lang === languages.en ? 'Make your resume more persuasive' : '让你的简历更有说服力',
    start: lang === languages.en ? 'Start Analysis' : '开始分析',
    desc:
      lang === languages.en
        ? 'Get your resume optimization report in under a minute.'
        : '1分钟内得出你的简历优化报告。',
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Box textAlign="center">
        <Typography variant="h3" component="h1" gutterBottom>
          {t.title}
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          {t.subtitle}
        </Typography>
        
        <Box sx={{ mt: 4 }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/upload')}
            sx={{ px: 4 }}
          >
            {t.start}
          </Button>
        </Box>

        <Box sx={{ mt: 4 }}>
          <Typography variant="body1">{t.desc}</Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default Home;
