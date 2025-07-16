import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Navbar from './components/Navbar';
import { LangProvider } from './contexts/LanguageContext';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Results from './pages/Results';
import Unauthorized from './pages/Unauthorized';
import Questionnaire from './pages/Questionnaire';
import Payment from './pages/Payment';
import About from './pages/About';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LangProvider>
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/results/:slug" element={<Results />} />
            <Route path="/questionnaire/:slug" element={<Questionnaire />} />
            <Route path="/payment/:slug" element={<Payment />} />
            <Route path="/unauthorized" element={<Unauthorized />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </Router>
      </LangProvider>
    </ThemeProvider>
  );
}

export default App;
