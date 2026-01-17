import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { Settings, Save } from '@mui/icons-material';

const Parameters = ({ parameters, onParametersChange }) => {
  const handleParameterChange = (field) => (event) => {
    const value = event.target.value;
    onParametersChange({ [field]: value });
  };

  const handleSavePreset = () => {
    // Guardar configuración en localStorage
    localStorage.setItem('arquitect-assistant-params', JSON.stringify(parameters));
    alert('Configuración guardada exitosamente');
  };

  const handleLoadPreset = () => {
    // Cargar configuración desde localStorage
    const saved = localStorage.getItem('arquitect-assistant-params');
    if (saved) {
      onParametersChange(JSON.parse(saved));
      alert('Configuración cargada exitosamente');
    } else {
      alert('No hay configuración guardada');
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom align="center">
        <Settings sx={{ mr: 2, verticalAlign: 'middle' }} />
        Configuración de Parámetros
      </Typography>

      <Grid container spacing={3}>
        {/* Main Parameters */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Parámetros Principales
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Número de Pisos Deseados"
                  type="number"
                  value={parameters.floors}
                  onChange={handleParameterChange('floors')}
                  inputProps={{ min: 1, max: 50 }}
                  helperText="Número de pisos que planea construir"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Tipo de Zona</InputLabel>
                  <Select
                    value={parameters.zone_type}
                    onChange={handleParameterChange('zone_type')}
                  >
                    <MenuItem value="residencial">Residencial</MenuItem>
                    <MenuItem value="comercial">Comercial</MenuItem>
                    <MenuItem value="industrial">Industrial</MenuItem>
                    <MenuItem value="mixto">Mixto</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Superficie Mínima por Vivienda (m²)"
                  type="number"
                  value={parameters.min_dwelling_area}
                  onChange={handleParameterChange('min_dwelling_area')}
                  inputProps={{ min: 20, max: 200, step: 0.1 }}
                  helperText="Mínimo legal en Chile: 40m²"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Altura Máxima Permitida (m)"
                  type="number"
                  value={parameters.max_height || ''}
                  onChange={handleParameterChange('max_height')}
                  inputProps={{ min: 3, max: 100, step: 0.1 }}
                  helperText="Dejar vacío para usar valor por defecto"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Zone Information */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Información por Zona
            </Typography>
            
            <Card variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" color="primary">
                  Residencial
                </Typography>
                <Typography variant="body2">
                  • Altura máx: 23m<br/>
                  • Coef. máx: 2.0<br/>
                  • Ocupación: 60%
                </Typography>
              </CardContent>
            </Card>
            
            <Card variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" color="secondary">
                  Comercial
                </Typography>
                <Typography variant="body2">
                  • Altura máx: 30m<br/>
                  • Coef. máx: 3.0<br/>
                  • Ocupación: 80%
                </Typography>
              </CardContent>
            </Card>
            
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" color="info">
                  Industrial
                </Typography>
                <Typography variant="body2">
                  • Altura máx: 25m<br/>
                  • Coef. máx: 2.5<br/>
                  • Ocupación: 70%
                </Typography>
              </CardContent>
            </Card>
          </Paper>
        </Grid>

        {/* Advanced Parameters */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Parámetros Avanzados
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Coeficiente de Constructibilidad"
                  type="number"
                  value={parameters.constructibility_coef || ''}
                  onChange={handleParameterChange('constructibility_coef')}
                  inputProps={{ min: 0.1, max: 5.0, step: 0.1 }}
                  helperText="Dejar vacío para usar valor del certificado"
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Porcentaje de Ocupación (%)"
                  type="number"
                  value={parameters.occupation_percentage || ''}
                  onChange={handleParameterChange('occupation_percentage')}
                  inputProps={{ min: 10, max: 100, step: 1 }}
                  helperText="Dejar vacío para usar valor del certificado"
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Superficie del Terreno (m²)"
                  type="number"
                  value={parameters.surface_area || ''}
                  onChange={handleParameterChange('surface_area')}
                  inputProps={{ min: 40, step: 0.1 }}
                  helperText="Solo para cálculos rápidos sin certificado"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Presets */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Configuración Rápida
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Save />}
                  onClick={handleSavePreset}
                >
                  Guardar Configuración Actual
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={handleLoadPreset}
                >
                  Cargar Configuración Guardada
                </Button>
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            <Typography variant="subtitle2" gutterBottom>
              Plantillas Predefinidas:
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Button
                  variant="text"
                  fullWidth
                  onClick={() => onParametersChange({
                    floors: 2,
                    zone_type: 'residencial',
                    min_dwelling_area: 40.0,
                    max_height: 6.5
                  })}
                >
                  Casa Residencial
                </Button>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  variant="text"
                  fullWidth
                  onClick={() => onParametersChange({
                    floors: 4,
                    zone_type: 'residencial',
                    min_dwelling_area: 40.0,
                    max_height: 12.0
                  })}
                >
                  Edificio Departamentos
                </Button>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  variant="text"
                  fullWidth
                  onClick={() => onParametersChange({
                    floors: 3,
                    zone_type: 'comercial',
                    min_dwelling_area: 60.0,
                    max_height: 12.0
                  })}
                >
                  Local Comercial
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Parameters;
