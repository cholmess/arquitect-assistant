import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import Upload from './components/Upload';
import Results from './components/Results';
import Parameters from './components/Parameters';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#388e3c',
    },
    error: {
      main: '#d32f2f',
    },
    warning: {
      main: '#f57c00',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [certificateData, setCertificateData] = useState(null);
  const [calculationResult, setCalculationResult] = useState(null);
  const [parameters, setParameters] = useState({
    floors: 3,
    zone_type: 'residencial',
    min_dwelling_area: 40.0
  });

  const handleCertificateProcessed = (data) => {
    setCertificateData(data);
  };

  const handleCalculationComplete = (result) => {
    setCalculationResult(result);
  };

  const handleParametersChange = (newParams) => {
    setParameters(prev => ({ ...prev, ...newParams }));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                🏗️ Arquitect Assistant - Cálculo de Cabidas OGUC
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route 
                path="/" 
                element={
                  <Box>
                    <Upload 
                      onCertificateProcessed={handleCertificateProcessed}
                      parameters={parameters}
                      onParametersChange={handleParametersChange}
                    />
                    {certificateData && (
                      <Results 
                        certificateData={certificateData}
                        calculationResult={calculationResult}
                        parameters={parameters}
                        onCalculationComplete={handleCalculationComplete}
                      />
                    )}
                  </Box>
                } 
              />
              <Route 
                path="/parameters" 
                element={
                  <Parameters 
                    parameters={parameters}
                    onParametersChange={handleParametersChange}
                  />
                } 
              />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
