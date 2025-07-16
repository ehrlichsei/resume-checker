import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
} from '@mui/material';
import TranslateIcon from '@mui/icons-material/Translate';
import { LangContext, languages } from '../contexts/LanguageContext';

const Navbar = () => {
  const { lang, toggle } = React.useContext(LangContext);

  const t = {
    title: lang === languages.en ? 'Resume Optimizer' : '简历优化器',
    upload: lang === languages.en ? 'Upload Resume' : '上传简历',
    about: lang === languages.en ? 'About' : '关于',
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={RouterLink} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
          {t.title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Button color="inherit" component={RouterLink} to="/upload">
            {t.upload}
          </Button>
          <Button color="inherit" component={RouterLink} to="/about">
            {t.about}
          </Button>
          <IconButton color="inherit" onClick={toggle} size="large">
            <TranslateIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
