import { Box, Paper, Typography, Alert, Chip } from '@mui/material';
import { Person as PersonIcon, SmartToy as BotIcon } from '@mui/icons-material';
import { RiskResultCard } from './RiskResultCard';
import { CodeViewer } from './CodeViewer';
import type { ChatResponse } from '@/services/api';

export interface ChatMessageData {
  id: string;
  role: 'user' | 'agent';
  content: string;
  response?: ChatResponse;
  timestamp: Date;
}

interface ChatMessageProps {
  message: ChatMessageData;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          maxWidth: '85%',
          display: 'flex',
          flexDirection: isUser ? 'row-reverse' : 'row',
          gap: 1,
          alignItems: 'flex-start',
        }}
      >
        {/* Avatar */}
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: isUser ? 'primary.main' : 'secondary.main',
            color: 'white',
            flexShrink: 0,
          }}
        >
          {isUser ? <PersonIcon fontSize="small" /> : <BotIcon fontSize="small" />}
        </Box>

        {/* Message content */}
        <Box sx={{ flex: 1 }}>
          {/* User message */}
          {isUser && (
            <Paper
              elevation={1}
              sx={{
                p: 1.5,
                backgroundColor: 'primary.main',
                color: 'primary.contrastText',
                borderRadius: 2,
              }}
            >
              <Typography variant="body2">{message.content}</Typography>
            </Paper>
          )}

          {/* Agent message */}
          {!isUser && message.response && (
            <Box>
              <Paper
                elevation={1}
                sx={{
                  p: 1.5,
                  backgroundColor: 'background.paper',
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                {/* Status indicator */}
                <Box sx={{ mb: 1 }}>
                  <Chip
                    label={message.response.status}
                    size="small"
                    color={
                      message.response.status === 'success'
                        ? 'success'
                        : message.response.status === 'error'
                          ? 'error'
                          : message.response.status === 'no_results'
                            ? 'warning'
                            : 'default'
                    }
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                </Box>

                {/* Answer text */}
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>
                  {message.response.answer}
                </Typography>

                {/* Error alert */}
                {message.response.error && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    <Typography variant="caption">{message.response.error}</Typography>
                  </Alert>
                )}

                {/* Risk results */}
                {message.response.answer_rows && message.response.answer_rows.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      {message.response.answer_rows.length} result{message.response.answer_rows.length !== 1 ? 's' : ''}
                    </Typography>
                    <Box sx={{ maxHeight: 400, overflowY: 'auto', pr: 0.5 }}>
                      {message.response.answer_rows.map((risk, idx) => (
                        <RiskResultCard key={idx} risk={risk} />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Code viewer */}
                {message.response.code && <CodeViewer code={message.response.code} />}

                {/* Execution log (debug) */}
                {message.response.execution_log && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace', fontSize: '0.65rem' }}>
                      {message.response.execution_log}
                    </Typography>
                  </Box>
                )}
              </Paper>

              {/* Timestamp */}
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5, ml: 1 }}>
                {message.timestamp.toLocaleTimeString()}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
};
