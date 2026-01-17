import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  Download,
  Assessment,
  Home,
  Business,
  Height
} from '@mui/icons-material';
import axios from 'axios';

const Results = ({ certificateData, calculationResult, parameters, onCalculationComplete }) => {
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportError, setReportError] = useState(null);

  if (!calculationResult) {
    return null;
  }

  const isApproved = calculationResult.compliance_status === 'APROBADO';
  const statusColor = isApproved ? 'success' : 'error';
  const statusIcon = isApproved ? <CheckCircle /> : <Error />;

  const generatePDFReport = async () => {
    setGeneratingReport(true);
    setReportError(null);

    try {
      const response = await axios.post('/api/v1/reports/generate-pdf', {
        certificate_data: certificateData,
        calculation_result: calculationResult,
        parameters: parameters
      }, {
        responseType: 'blob'
      });

      // Crear URL y descargar el PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'informe_cabida_oguc.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setReportError('Error generando el reporte PDF');
    } finally {
      setGeneratingReport(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('es-CL').format(num);
  };

  const resultsData = [
    {
      label: 'Cabida Máxima',
      value: `${formatNumber(calculationResult.max_building_surface)} m²`,
      icon: <Business />,
      color: 'primary'
    },
    {
      label: 'Unidades de Vivienda',
      value: calculationResult.dwelling_units_max,
      icon: <Home />,
      color: 'secondary'
    },
    {
      label: 'Pisos Permitidos',
      value: calculationResult.allowed_floors,
      icon: <Height />,
      color: 'info'
    },
    {
      label: 'Utilización Coeficiente',
      value: `${calculationResult.constructibility_utilization.toFixed(1)}%`,
      icon: <Assessment />,
      color: calculationResult.constructibility_utilization > 70 ? 'success' : 'warning'
    }
  ];

  const detailedResults = [
    ['Superficie Total Terreno', `${formatNumber(calculationResult.total_surface)} m²`],
    ['Cabida Máxima Edificación', `${formatNumber(calculationResult.max_building_surface)} m²`],
    ['Superficie Máxima Emplazamiento', `${formatNumber(calculationResult.max_occupation_surface)} m²`],
    ['Altura Máxima Permitida', `${formatNumber(calculationResult.max_height)} m`],
    ['Pisos Permitidos', calculationResult.allowed_floors],
    ['Unidades Vivienda Máximas', calculationResult.dwelling_units_max],
    ['Utilización Coeficiente', `${calculationResult.constructibility_utilization.toFixed(1)}%`]
  ];

  return (
    <Box sx={{ mt: 4 }}>
      {/* Status Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <Chip
              icon={statusIcon}
              label={isApproved ? 'APROBADO' : 'RECHAZADO'}
              color={statusColor}
              sx={{ fontSize: '1.1rem', py: 2, px: 3 }}
            />
          </Box>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={generatePDFReport}
            disabled={generatingReport}
          >
            {generatingReport ? 'Generando...' : 'Descargar Informe PDF'}
          </Button>
        </Box>
        
        {reportError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {reportError}
          </Alert>
        )}
      </Paper>

      {/* Results Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {resultsData.map((item, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box color={`${item.color}.main`} mr={1}>
                    {item.icon}
                  </Box>
                  <Typography variant="h6" color="text.secondary">
                    {item.label}
                  </Typography>
                </Box>
                <Typography variant="h4" component="div">
                  {item.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Detailed Results Table */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          📊 Resultados Detallados
        </Typography>
        <TableContainer>
          <Table>
            <TableBody>
              {detailedResults.map((row, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                    {row[0]}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {row[1]}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Rejection Reasons */}
      {calculationResult.rejection_reasons && calculationResult.rejection_reasons.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom color="error">
            ❌ Motivos de Rechazo
          </Typography>
          <List>
            {calculationResult.rejection_reasons.map((reason, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Error color="error" />
                </ListItemIcon>
                <ListItemText primary={reason} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Recommendations */}
      {calculationResult.recommendations && calculationResult.recommendations.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            💡 Recomendaciones
          </Typography>
          <List>
            {calculationResult.recommendations.map((recommendation, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {recommendation.includes('✅') ? (
                    <CheckCircle color="success" />
                  ) : recommendation.includes('❌') ? (
                    <Error color="error" />
                  ) : recommendation.includes('📊') ? (
                    <Assessment color="info" />
                  ) : recommendation.includes('🏠') ? (
                    <Home color="primary" />
                  ) : (
                    <Info color="info" />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary={recommendation}
                  primaryTypographyProps={{
                    style: { whiteSpace: 'pre-line' }
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Progress Indicators */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          📈 Indicadores de Rendimiento
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Utilización del Coeficiente</Typography>
            <Typography variant="body2">{calculationResult.constructibility_utilization.toFixed(1)}%</Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={Math.min(calculationResult.constructibility_utilization, 100)}
            color={calculationResult.constructibility_utilization > 70 ? 'success' : 'warning'}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Pisos Utilizados vs Permitidos</Typography>
            <Typography variant="body2">{parameters.floors} / {calculationResult.allowed_floors}</Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={(parameters.floors / calculationResult.allowed_floors) * 100}
            color={parameters.floors <= calculationResult.allowed_floors ? 'success' : 'error'}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        <Box>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Densidad de Construcción</Typography>
            <Typography variant="body2">
              {((calculationResult.max_building_surface / calculationResult.total_surface) * 100).toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={(calculationResult.max_building_surface / calculationResult.total_surface) * 100}
            color="primary"
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default Results;
