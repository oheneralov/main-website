import React, { useCallback, useEffect, useRef, useState } from 'react';
import './ChatbotDock.css';

type ChatMessage = {
  id: number;
  role: 'assistant' | 'user';
  text: string;
};

type RagQueryResult = {
  id: string;
  document: string;
  similarity_score?: number;
  metadata?: Record<string, unknown>;
};

type RagQueryResponse = {
  query: string;
  num_documents: number;
  results: RagQueryResult[];
  context: string;
  llm_prompt: string;
};

const initialMessages: ChatMessage[] = [
  {
    id: 1,
    role: 'assistant',
    text: 'Hi, I am AlexBot — I can walk you through my AWS playbook anytime.',
  }
];

const quickPrompts = [
  'What service do you offer?',
];

const DEFAULT_RAG_BASE_URL = 'http://localhost:8000';
const RAG_BASE_URL = (import.meta.env.VITE_RAG_API_BASE_URL ?? DEFAULT_RAG_BASE_URL).replace(/\/$/, '');
const RAG_QUERY_URL = `${RAG_BASE_URL}/query`;
const DEFAULT_RETRIEVAL_K = 4;

const ChatbotDock: React.FC = () => {
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [position, setPosition] = useState<{ x: number; y: number } | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRagOnline, setIsRagOnline] = useState<boolean | null>(null);
  const dockRef = useRef<HTMLDivElement>(null);
  const dragOrigin = useRef<{ startX: number; startY: number; originX: number; originY: number } | null>(null);
  const messageIdRef = useRef(initialMessages.length + 1);

  const clampPosition = useCallback((candidateX: number, candidateY: number) => {
    if (typeof window === 'undefined') {
      return { x: candidateX, y: candidateY };
    }
    const dock = dockRef.current;
    const width = dock?.offsetWidth ?? 360;
    const height = dock?.offsetHeight ?? 520;
    const minX = 16;
    const minY = 16;
    const maxX = Math.max(minX, window.innerWidth - width - 16);
    const maxY = Math.max(minY, window.innerHeight - height - 16);
    return {
      x: Math.min(Math.max(candidateX, minX), maxX),
      y: Math.min(Math.max(candidateY, minY), maxY),
    };
  }, []);

  // Check if RAG is online on mount
  useEffect(() => {
    const checkRagOnline = async () => {
      try {
        const response = await fetch(RAG_BASE_URL + '/health', { method: 'GET' });
        if (response.ok) {
          setIsRagOnline(true);
        } else {
          setIsRagOnline(false);
        }
      } catch {
        setIsRagOnline(false);
      }
    };
    checkRagOnline();
  }, []);

  useEffect(() => {
    if (position || !dockRef.current) {
      return;
    }
    const rect = dockRef.current.getBoundingClientRect();
    setPosition(clampPosition(rect.left, rect.top));
  }, [position, clampPosition]);

  useEffect(() => {
    if (!isDragging) {
      return;
    }

    const handlePointerMove = (event: PointerEvent) => {
      if (!dragOrigin.current) {
        return;
      }
      const { startX, startY, originX, originY } = dragOrigin.current;
      const next = clampPosition(
        originX + (event.clientX - startX),
        originY + (event.clientY - startY)
      );
      setPosition(next);
    };

    const handlePointerUp = () => {
      setIsDragging(false);
      dragOrigin.current = null;
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
    };
  }, [isDragging, clampPosition]);

  useEffect(() => {
    if (!position) {
      return;
    }

    const handleResize = () => {
      setPosition((current) => {
        if (!current) {
          return current;
        }
        return clampPosition(current.x, current.y);
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [position, clampPosition]);

  const handleDragStart = (event: React.PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0 && event.pointerType !== 'touch') {
      return;
    }
    event.preventDefault();

    const rect = dockRef.current?.getBoundingClientRect();
    let basePosition = position;

    if (!basePosition && rect) {
      basePosition = clampPosition(rect.left, rect.top);
      setPosition(basePosition);
    } else if (!basePosition) {
      basePosition = { x: 0, y: 0 };
      setPosition(basePosition);
    }

    if (!basePosition) {
      return;
    }

    dragOrigin.current = {
      startX: event.clientX,
      startY: event.clientY,
      originX: basePosition.x,
      originY: basePosition.y,
    };
    setIsDragging(true);
  };

  const dockStyle = position
    ? { left: `${position.x}px`, top: `${position.y}px`, right: 'auto', bottom: 'auto' }
    : undefined;

  const toggleTheme = () => {
    setTheme((current) => (current === 'light' ? 'dark' : 'light'));
  };

  const sendQueryToRag = async (input: string) => {
    if (isLoading) {
      return;
    }

    const trimmed = input.trim();
    if (!trimmed) {
      return;
    }

    const userMessage: ChatMessage = {
      id: messageIdRef.current++,
      role: 'user',
      text: trimmed,
    };

    setMessages((current) => [...current, userMessage]);
    setDraft('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(RAG_QUERY_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: trimmed, k: DEFAULT_RETRIEVAL_K }),
      });

      const payloadText = await response.text();
      if (!response.ok) {
        let detail = payloadText;
        try {
          const parsed = payloadText ? JSON.parse(payloadText) : null;
          detail = parsed?.detail ?? detail;
        } catch {
          // Ignore JSON parse errors for non-JSON payloads
        }
        throw new Error(detail || `Request failed with status ${response.status}`);
      }

      if (!payloadText) {
        throw new Error('Received empty response from the RAG service.');
      }

      const data = JSON.parse(payloadText) as RagQueryResponse;
      const retrievedCount = data.num_documents ?? data.results?.length ?? 0;
      const contextText = data.context?.trim();
      const assistantText = contextText
        ? `${contextText}\n\nRetrieved ${retrievedCount} chunk${retrievedCount === 1 ? '' : 's'} from the knowledge base.`
        : 'I could not find relevant context for that question.';

      const assistantMessage: ChatMessage = {
        id: messageIdRef.current++,
        role: 'assistant',
        text: assistantText,
      };
      setMessages((current) => [...current, assistantMessage]);
    } catch (requestError) {
      const fallbackMessage =
        requestError instanceof Error
          ? requestError.message
          : 'Failed to reach the RAG service.';

      setError(fallbackMessage);
      const assistantMessage: ChatMessage = {
        id: messageIdRef.current++,
        role: 'assistant',
        text: "I couldn't connect to the knowledge base right now. Please try again shortly.",
      };
      setMessages((current) => [...current, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await sendQueryToRag(draft);
  };

  const handlePromptClick = (prompt: string) => {
    void sendQueryToRag(prompt);
  };

  // Only show chatbot if RAG is online
  if (isRagOnline === null) {
    // Still checking
    return (
      <div className="chatbot-dock chatbot-dock-loading" aria-live="polite" style={{ left: 16, top: 16 }}>
        <div className="footer-chat-card">
          <p>Checking knowledge base status...</p>
        </div>
      </div>
    );
  }
  if (!isRagOnline) {
    // RAG is offline
    return (
      <div className="chatbot-dock chatbot-dock-error" aria-live="polite" style={{ left: 16, top: 16 }}>
        <div className="footer-chat-card">
          <p className="footer-chat-error" role="alert">
            The knowledge base is currently offline. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  // ...existing code...
  return (
    <div
      className={`chatbot-dock theme-${theme}${isDragging ? ' is-dragging' : ''}`}
      aria-live="polite"
      aria-label="AlexBot chat dock"
      ref={dockRef}
      style={dockStyle}
    >
      <div className="footer-chat-card" id="chat-with-me">
        <div
          className="footer-chat-header"
          onPointerDown={handleDragStart}
          aria-label="Drag to move chat window"
        >
          <div>
            <p className="footer-chat-eyebrow">Chat live</p>
            <h6>Ask AlexBot</h6>
            <p>
              Ask me about services I provide, my experience, or how I can help your business.
            </p>
          </div>
          <div className="footer-chat-controls">
            <div className="footer-chat-status">
              <span className="footer-status-dot" aria-hidden="true"></span>
              <span>Online</span>
            </div>
            <button
              type="button"
              className="footer-chat-theme-toggle"
              onClick={toggleTheme}
              aria-pressed={theme === 'dark'}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              {theme === 'light' ? 'Dark mode' : 'Light mode'}
            </button>
          </div>
        </div>

        <div className="footer-chat-messages" role="log" aria-live="polite">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`footer-chat-message ${
                message.role === 'user' ? 'is-user' : 'is-assistant'
              }`}
            >
              <span className="footer-chat-author">
                {message.role === 'user' ? 'You' : 'AlexBot'}
              </span>
              <p>{message.text}</p>
            </div>
          ))}
        </div>

        <div className="footer-chat-prompts" aria-label="Suggested prompts">
          {quickPrompts.map((prompt, index) => (
            <button
              type="button"
              key={prompt}
              onClick={() => handlePromptClick(prompt)}
              disabled={isLoading}
            >
              <span>0{index + 1}</span>
              {prompt}
            </button>
          ))}
        </div>

        <form
          className="footer-chat-form"
          onSubmit={handleSubmit}
          aria-busy={isLoading}
        >
          <input
            type="text"
            placeholder="Type a message to AlexBot"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            aria-label="Chat message"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>

        {(isLoading || error) && (
          <div className="footer-chat-feedback">
            {isLoading && (
              <p className="footer-chat-loading" aria-live="polite">
                Contacting the knowledge base...
              </p>
            )}
            {error && (
              <p className="footer-chat-error" role="alert">
                {error}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatbotDock;
