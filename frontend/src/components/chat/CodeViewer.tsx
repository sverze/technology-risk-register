import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Collapse,
  Tooltip,
} from '@mui/material';
import {
  Code as CodeIcon,
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';

interface CodeViewerProps {
  code: string;
  language?: string;
}

export const CodeViewer: React.FC<CodeViewerProps> = ({ code, language = 'python' }) => {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  return (
    <Box sx={{ mt: 1 }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          cursor: 'pointer',
          '&:hover': { opacity: 0.8 },
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <CodeIcon fontSize="small" color="action" />
        <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
          Generated Code ({language})
        </Typography>
        <Tooltip title={copied ? 'Copied!' : 'Copy code'}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleCopy();
            }}
            sx={{ mr: 0.5 }}
          >
            <CopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <IconButton
          size="small"
          sx={{
            transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s',
          }}
        >
          <ExpandMoreIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Code content */}
      <Collapse in={expanded}>
        <Paper
          elevation={0}
          sx={{
            mt: 1,
            p: 1.5,
            backgroundColor: 'grey.900',
            borderRadius: 1,
            maxHeight: 400,
            overflow: 'auto',
          }}
        >
          <pre
            style={{
              margin: 0,
              fontFamily: '"Fira Code", "Courier New", monospace',
              fontSize: '0.75rem',
              lineHeight: 1.5,
              color: '#f8f8f2',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {code}
          </pre>
        </Paper>
      </Collapse>
    </Box>
  );
};
