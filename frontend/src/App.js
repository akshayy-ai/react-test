
import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  TextField,
  Box,
  Paper,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Snackbar,
  Alert,
  Chip,
  Grid,
  IconButton
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {
  UploadFile as UploadFileIcon,
  Send as SendIcon,
  SmartToy as SmartToyIcon,
  Clear as ClearIcon
} from '@mui/icons-material';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#9c27b0' },
  },
});

const backendUrl = 'http://localhost:8000';

const quickQuestions = [
  "What is this document about?",
  "What are the main requirements?",
  "What are the key deliverables?",
  "What is the timeline mentioned?"
];

export default function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sourceDocs, setSourceDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [isDocumentUploaded, setIsDocumentUploaded] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setAnswer('');
    setSourceDocs([]);
    setIsDocumentUploaded(false);
  };

  const handleUpload = async () => {
    if (!file) {
      setSnackbar({ open: true, message: 'Please select a file first', severity: 'warning' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);

    try {
      const response = await fetch(`${backendUrl}/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      if (response.ok) {
        setSnackbar({ open: true, message: `✅ Upload successful: ${data.filename}`, severity: 'success' });
        setIsDocumentUploaded(true);
      } else {
        setSnackbar({ open: true, message: `❌ Upload failed: ${data.detail}`, severity: 'error' });
      }
    } catch (error) {
      setSnackbar({ open: true, message: `❌ Error: ${error.message}`, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) {
      setSnackbar({ open: true, message: 'Please enter a question', severity: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });

      const data = await response.json();
      if (response.ok) {
        setAnswer(data.answer);
        setSourceDocs(data.source_documents || []);
        setSnackbar({ open: true, message: '✅ Answer received', severity: 'success' });
      } else {
        setSnackbar({ open: true, message: `❌ Error: ${data.detail}`, severity: 'error' });
      }
    } catch (error) {
      setSnackbar({ open: true, message: `❌ Error: ${error.message}`, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Paper 
          elevation={0} 
          sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            p: 4,
            mb: 4,
            borderRadius: 3
          }}
        >
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <SmartToyIcon sx={{ fontSize: 48, mr: 2 }} />
            <Typography variant="h3" component="h1" fontWeight="bold">
              RAG Document QA System
            </Typography>
          </Box>
          <Typography variant="h6" align="center" sx={{ opacity: 0.9 }}>
            Upload documents and get AI-powered insights
          </Typography>
        </Paper>

        <Grid container spacing={3}>
          {/* Upload Section */}
          <Grid item xs={12} md={6}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📄 Document Upload
                </Typography>
                
                <Button
                  variant="outlined"
                  component="label"
                  fullWidth
                  startIcon={<UploadFileIcon />}
                  sx={{ p: 2, mb: 2, borderStyle: 'dashed' }}
                >
                  {file ? file.name : 'Choose PDF, TXT, or MD file'}
                  <input
                    type="file"
                    hidden
                    accept=".pdf,.txt,.md"
                    onChange={handleFileChange}
                  />
                </Button>

                <Button
                  variant="contained"
                  onClick={handleUpload}
                  disabled={!file || loading}
                  fullWidth
                  size="large"
                  startIcon={loading ? <CircularProgress size={20} /> : <UploadFileIcon />}
                >
                  {loading ? 'Processing...' : 'Upload & Process'}
                </Button>

                {isDocumentUploaded && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    Document ready for questions! 🎉
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Question Section */}
          <Grid item xs={12} md={6}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ❓ Ask Questions
                </Typography>

                <TextField
                  label="Enter your question"
                  multiline
                  minRows={4}
                  fullWidth
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  disabled={loading}
                  sx={{ mb: 2 }}
                />

                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Quick Questions:
                  </Typography>
                  {quickQuestions.map((q, index) => (
                    <Chip
                      key={index}
                      label={q}
                      onClick={() => setQuestion(q)}
                      size="small"
                      variant="outlined"
                      clickable
                      sx={{ m: 0.5 }}
                    />
                  ))}
                </Box>

                <Button
                  variant="contained"
                  color="secondary"
                  onClick={handleAsk}
                  disabled={!question.trim() || loading || !isDocumentUploaded}
                  fullWidth
                  size="large"
                  endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                >
                  {loading ? 'Thinking...' : 'Get Answer'}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Answer Section */}
          {answer && (
            <Grid item xs={12}>
              <Card elevation={3}>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                    <Typography variant="h6">💡 AI Answer</Typography>
                    <IconButton onClick={() => {setAnswer(''); setSourceDocs([]); setQuestion('');}}>
                      <ClearIcon />
                    </IconButton>
                  </Box>

                  <Paper elevation={1} sx={{ p: 3, bgcolor: 'grey.50', mb: 3 }}>
                    <Typography variant="body1" sx={{ lineHeight: 1.7 }}>
                      {answer}
                    </Typography>
                  </Paper>

                  {sourceDocs.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" gutterBottom>
                        📖 Source References ({sourceDocs.length})
                      </Typography>
                      <List>
                        {sourceDocs.map((doc, index) => (
                          <ListItem key={index} divider>
                            <ListItemText
                              primary={`Chunk ${index + 1}`}
                              secondary={doc.content}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({...snackbar, open: false})}
        >
          <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </ThemeProvider>
  );
}
