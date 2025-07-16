// src/pages/Unauthorized.js
import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Unauthorized = () => {
  const navigate = useNavigate();
  return (
    <Box textAlign="center" mt={10}>
      <Typography variant="h4" gutterBottom>
        401 / 403
      </Typography>
      <Typography variant="h6" gutterBottom>
        未授权访问 / Unauthorized Access
      </Typography>
      <Button variant="contained" onClick={() => navigate('/')}>返回首页 / Home</Button>
    </Box>
  );
};

export default Unauthorized;
