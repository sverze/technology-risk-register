import { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import { ChatMessage } from '@/components/chat/ChatMessage';
import type { ChatMessageData } from '@/components/chat/ChatMessage';
import { ChatInput } from '@/components/chat/ChatInput';
import type { ChatOptions } from '@/components/chat/ChatInput';
import { chatApi } from '@/services/api';
import type { ChatResponse } from '@/services/api';

const STORAGE_KEY = 'risk-chat-history';

export const RiskChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        // Convert timestamp strings back to Date objects
        const messagesWithDates = parsed.map((msg: { timestamp: string | Date; [key: string]: unknown }) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(messagesWithDates as ChatMessageData[]);
      }
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  }, []);

  // Save chat history to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
      } catch (err) {
        console.error('Failed to save chat history:', err);
      }
    }
  }, [messages]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (content: string, options: ChatOptions) => {
    setError(null);

    // Add user message
    const userMessage: ChatMessageData = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send to API
    setLoading(true);
    try {
      const response: ChatResponse = await chatApi.sendMessage({
        question: content,
        model: options.model,
        temperature: options.temperature,
        show_code: options.showCode,
      });

      // Add agent response
      const agentMessage: ChatMessageData = {
        id: `agent-${Date.now()}`,
        role: 'agent',
        content: response.answer,
        response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (err: unknown) {
      const error = err as { message?: string };
      setError(error.message || 'Failed to send message. Please try again.');
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    if (confirm('Are you sure you want to clear the conversation history?')) {
      setMessages([]);
      localStorage.removeItem(STORAGE_KEY);
      setError(null);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 180px)' }}>
      {/* Header */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Risk SME Chat
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Ask questions about your technology risks using natural language. The AI agent will query the database and provide
          answers with actionable insights.
        </Typography>
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Messages area */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          p: 2,
          mb: 2,
          overflowY: 'auto',
          backgroundColor: 'background.default',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 2,
          minHeight: 300,
        }}
      >
        {messages.length === 0 && !loading && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center',
            }}
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Welcome to Risk SME Chat
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 500 }}>
              Start by asking a question about your risks. For example, try asking about critical risks, financial impacts,
              technology domains, or overdue reviews.
            </Typography>
          </Box>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <CircularProgress size={24} />
            <Typography variant="body2" color="text.secondary">
              Thinking...
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <div ref={messagesEndRef} />
      </Paper>

      {/* Input area */}
      <Box>
        <ChatInput onSend={handleSend} onClear={handleClear} disabled={loading} />
      </Box>
    </Box>
  );
};
