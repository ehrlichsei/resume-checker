// src/pages/About.js
import React, { useContext } from 'react';
import { Container, Typography, Link, Box } from '@mui/material';
import { LangContext, languages } from '../contexts/LanguageContext';

const About = () => {
  const { lang } = useContext(LangContext);

  const t = {
    title: lang === languages.en ? 'About' : '关于',
    guideLabel: lang === languages.en ? 'Job hunting guide:' : '求职攻略请查看',
    guideUrl: 'https://kittybro.notion.site/offer-hunter',
    contact: lang === languages.en
      ? 'If you find any issue, please contact admin '
      : '如果发现有问题，请联系管理员 ',
    contactTail: lang === languages.en ? ', or WeChat fangyuli0117' : '，或者微信 fangyuli0117',
    email: 'hello@yulifang.dev',
    featureIntro: lang === languages.en
      ? 'This tool provides three key outputs:'
      : '本简历分析工具将为你生成三方面的结果：',
    features: lang === languages.en
      ? [
          'Potential career directions',
          'Suggested position titles for each experience',
          'Optimized wording for your experience descriptions',
        ]
      : [
          '求职的可能性方向',
          '每段工作经历的职位 Title 建议',
          '工作经历描述优化',
        ],
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        {t.title}
      </Typography>
      <Box my={3}>
        <Typography variant="body1" paragraph>
          {t.guideLabel}{' '}
          <Link href={t.guideUrl} target="_blank" rel="noopener noreferrer">
            {t.guideUrl}
          </Link>
        </Typography>
        <Typography variant="body1" paragraph>
          {t.contact}
          <Link href={`mailto:${t.email}`}>{t.email}</Link>
          {t.contactTail}
        </Typography>
        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          {t.featureIntro}
        </Typography>
        <Typography component="ol" sx={{ pl: 3 }}>
          {t.features.map((f, idx) => (
            <li key={idx}>{f}</li>
          ))}
        </Typography>
      </Box>
    </Container>
  );
};

export default About;
