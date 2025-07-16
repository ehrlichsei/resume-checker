import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import axios from 'axios';

const Questionnaire = () => {
  const navigate = useNavigate();
  const { slug } = useParams();
  const [formData, setFormData] = useState({
    current_status: '',
    job_type: '',
    salary_expectation: '',
    preferred_location: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await axios.post(`/api/questionnaire/${slug}`, formData);
      navigate(`/payment/${slug}`);
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Job Preferences Questionnaire
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1">Current Employment Status</Typography>
            <Select
              fullWidth
              name="current_status"
              value={formData.current_status}
              onChange={handleChange}
              margin="normal"
              required
            >
              <MenuItem value="employed">Currently Employed</MenuItem>
              <MenuItem value="unemployed">Unemployed</MenuItem>
              <MenuItem value="student">Student</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1">Preferred Job Type</Typography>
            <Select
              fullWidth
              name="job_type"
              value={formData.job_type}
              onChange={handleChange}
              margin="normal"
              required
            >
              <MenuItem value="full_time">Full-time</MenuItem>
              <MenuItem value="part_time">Part-time</MenuItem>
              <MenuItem value="contract">Contract</MenuItem>
              <MenuItem value="remote">Remote</MenuItem>
              <MenuItem value="hybrid">Hybrid</MenuItem>
            </Select>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1">Salary Expectation (USD)</Typography>
            <TextField
              fullWidth
              name="salary_expectation"
              type="number"
              value={formData.salary_expectation}
              onChange={handleChange}
              margin="normal"
              required
              inputProps={{ min: 0 }}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1">Preferred Location</Typography>
            <TextField
              fullWidth
              name="preferred_location"
              value={formData.preferred_location}
              onChange={handleChange}
              margin="normal"
              required
            />
          </Box>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 3 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        </form>
      </Paper>
    </Container>
  );
};

export default Questionnaire;
