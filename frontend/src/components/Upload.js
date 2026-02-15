import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent
} from '@mui/material';
import { CloudUpload, CheckCircle, Error } from '@mui/icons-material';
import axios from 'axios';

const Upload = ({ onCertificateProcessed, onCalculationComplete, parameters, onParametersChange }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const steps = ['Subir Certificado', 'Configurar Parámetros', 'Procesar'];

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setActiveStep(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('floors', parameters.floors);
      formData.append('zone_type', parameters.zone_type);
      formData.append('min_dwelling_area', parameters.min_dwelling_area);

      const response = await axios.post('/api/v1/upload/certificate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadResult(response.data);
        setActiveStep(2);
        onCertificateProcessed(response.data.certificate_data);
      } else {
        setError(response.data.message || 'Error procesando el certificado');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error en la conexión con el servidor');
    } finally {
      setUploading(false);
    }
  }, [parameters, onCertificateProcessed]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleParameterChange = (field) => (event) => {
    const value = event.target.value;
    onParametersChange({ [field]: value });
    if (uploadResult) {
      setActiveStep(1);
    }
  };

  const handleProcess = async () => {
    if (!uploadResult) return;

    setUploading(true);
    setError(null);

    try {
      const response = await axios.post('/api/v1/calculate/cabida', {
        certificate_data: uploadResult.certificate_data,
        floors: parameters.floors,
        zone_type: parameters.zone_type,
        min_dwelling_area: parameters.min_dwelling_area
      });

      if (response.data) {
        setUploadResult(prev => ({ ...prev, calculation_result: response.data }));
        if (onCalculationComplete) {
          onCalculationComplete(response.data);
        }
        setActiveStep(2);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error en el cálculo');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom align="center">
        Sistema de Cálculo de Cabidas OGUC
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Grid container spacing={3}>
        {/* Upload Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              1. Subir Certificado de Informaciones Previas
            </Typography>
            
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  bgcolor: 'action.hover',
                  borderColor: 'primary.main',
                }
              }}
            >
              <input {...getInputProps()} />
              <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              {isDragActive ? (
                <Typography>Suelta el archivo aquí...</Typography>
              ) : (
                <Box>
                  <Typography>
                    Arrastra tu certificado aquí o haz clic para seleccionar
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    PDF, JPG o PNG (Máx. 10MB)
                  </Typography>
                </Box>
              )}
            </Box>

            {uploading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <CircularProgress />
              </Box>
            )}

            {uploadResult && (
              <Alert 
                icon={<CheckCircle />}
                severity="success" 
                sx={{ mt: 2 }}
              >
                Certificado procesado exitosamente
              </Alert>
            )}

            {error && (
              <Alert 
                icon={<Error />}
                severity="error" 
                sx={{ mt: 2 }}
              >
                {error}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Parameters Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              2. Configurar Parámetros de Cálculo
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Número de Pisos"
                  type="number"
                  value={parameters.floors}
                  onChange={handleParameterChange('floors')}
                  inputProps={{ min: 1, max: 50 }}
                  disabled={uploading}
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth>
                  <InputLabel>Tipo de Zona</InputLabel>
                  <Select
                    value={parameters.zone_type}
                    onChange={handleParameterChange('zone_type')}
                    disabled={uploading}
                  >
                    <MenuItem value="residencial">Residencial</MenuItem>
                    <MenuItem value="comercial">Comercial</MenuItem>
                    <MenuItem value="industrial">Industrial</MenuItem>
                    <MenuItem value="mixto">Mixto</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Superficie Mínima (m²)"
                  type="number"
                  value={parameters.min_dwelling_area}
                  onChange={handleParameterChange('min_dwelling_area')}
                  inputProps={{ min: 20, max: 200, step: 0.1 }}
                  disabled={uploading}
                />
              </Grid>
            </Grid>

            {uploadResult && !uploadResult.calculation_result && (
              <Button
                variant="contained"
                fullWidth
                onClick={handleProcess}
                disabled={uploading}
                sx={{ mt: 3 }}
              >
                {uploading ? <CircularProgress size={24} /> : 'Calcular Cabida'}
              </Button>
            )}
          </Paper>
        </Grid>

        {/* Certificate Data Preview */}
        {uploadResult?.certificate_data && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📋 Datos Extraídos del Certificado
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Rol:</strong> {uploadResult.certificate_data.rol || 'No especificado'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Superficie:</strong> {uploadResult.certificate_data.superficie_terreno || 0} m²
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Comuna:</strong> {uploadResult.certificate_data.comuna || 'No especificada'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Dirección:</strong> {uploadResult.certificate_data.direccion || 'No especificada'}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Upload;
