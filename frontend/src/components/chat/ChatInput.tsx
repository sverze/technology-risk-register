import { useState } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Tooltip,
  Menu,
  FormControlLabel,
  Switch,
  Slider,
  Typography,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  Settings as SettingsIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';

interface ChatInputProps {
  onSend: (message: string, options: ChatOptions) => void;
  onClear: () => void;
  disabled?: boolean;
}

export interface ChatOptions {
  showCode: boolean;
  temperature: number;
  model: string;
}

const EXAMPLE_QUESTIONS = [
  'Show me all critical risks',
  'What risks have financial impact > $500000?',
  'List infrastructure risks that are overdue for review',
  'Show risks by technology domain',
  'Which risks affect business services?',
];

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, onClear, disabled = false }) => {
  const [input, setInput] = useState('');
  const [options, setOptions] = useState<ChatOptions>({
    showCode: false,
    temperature: 0.2,
    model: 'claude-sonnet-4-5-20250929',
  });
  const [settingsAnchor, setSettingsAnchor] = useState<null | HTMLElement>(null);

  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSend(trimmed, options);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleExampleClick = (question: string) => {
    setInput(question);
  };

  const handleSettingsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setSettingsAnchor(event.currentTarget);
  };

  const handleSettingsClose = () => {
    setSettingsAnchor(null);
  };

  return (
    <Box>
      {/* Example questions */}
      {input.length === 0 && (
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ width: '100%', mb: 0.5 }}>
            Example questions:
          </Typography>
          {EXAMPLE_QUESTIONS.map((question, idx) => (
            <Chip
              key={idx}
              label={question}
              size="small"
              onClick={() => handleExampleClick(question)}
              sx={{
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'primary.light',
                  color: 'primary.contrastText',
                },
              }}
            />
          ))}
        </Box>
      )}

      {/* Input field */}
      <Paper elevation={2} sx={{ p: 1, display: 'flex', alignItems: 'flex-end', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Ask me anything about risks... (Press Enter to send, Shift+Enter for new line)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          variant="outlined"
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': {
              paddingRight: 0,
            },
          }}
        />

        {/* Settings button */}
        <Tooltip title="Settings">
          <IconButton size="small" onClick={handleSettingsOpen} disabled={disabled}>
            <SettingsIcon />
          </IconButton>
        </Tooltip>

        {/* Clear button */}
        <Tooltip title="Clear conversation">
          <IconButton size="small" onClick={onClear} disabled={disabled}>
            <ClearIcon />
          </IconButton>
        </Tooltip>

        {/* Send button */}
        <Tooltip title="Send message">
          <span>
            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={disabled || !input.trim()}
              sx={{
                backgroundColor: 'primary.main',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                },
                '&:disabled': {
                  backgroundColor: 'action.disabledBackground',
                },
              }}
            >
              <SendIcon />
            </IconButton>
          </span>
        </Tooltip>
      </Paper>

      {/* Settings menu */}
      <Menu anchorEl={settingsAnchor} open={Boolean(settingsAnchor)} onClose={handleSettingsClose}>
        <Box sx={{ p: 2, minWidth: 280 }}>
          <Typography variant="subtitle2" gutterBottom>
            Chat Settings
          </Typography>

          {/* Show code toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={options.showCode}
                onChange={(e) =>
                  setOptions((prev) => ({
                    ...prev,
                    showCode: e.target.checked,
                  }))
                }
                size="small"
              />
            }
            label={<Typography variant="body2">Show generated code</Typography>}
            sx={{ mb: 2, display: 'block' }}
          />

          {/* Temperature slider */}
          <Typography variant="body2" gutterBottom>
            Temperature: {options.temperature.toFixed(1)}
          </Typography>
          <Slider
            value={options.temperature}
            onChange={(_, value) =>
              setOptions((prev) => ({
                ...prev,
                temperature: value as number,
              }))
            }
            min={0}
            max={1}
            step={0.1}
            marks={[
              { value: 0, label: '0' },
              { value: 0.5, label: '0.5' },
              { value: 1, label: '1' },
            ]}
            valueLabelDisplay="auto"
            size="small"
          />
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
            Higher values make output more creative, lower values more deterministic
          </Typography>
        </Box>
      </Menu>
    </Box>
  );
};
