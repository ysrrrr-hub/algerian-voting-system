// dashboard/src/hooks/useSocket.ts
// Custom hook لإدارة اتصال Socket.IO والتحديثات الحية

import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

export interface NewVoteEvent {
  blockchain_length: number;
  timestamp:         string;
}

export interface SocketState {
  connected:    boolean;
  lastVoteTime: string | null;
  voteCount:    number;
  error:        string | null;
}

interface UseSocketOptions {
  url:            string;
  onNewVote?:     (event: NewVoteEvent) => void;
  autoConnect?:   boolean;
}

export function useSocket({
  url,
  onNewVote,
  autoConnect = true,
}: UseSocketOptions) {
  const socketRef = useRef<Socket | null>(null);

  const [state, setState] = useState<SocketState>({
    connected:    false,
    lastVoteTime: null,
    voteCount:    0,
    error:        null,
  });

  const connect = useCallback(() => {
    if (socketRef.current?.connected) return;

    const socket = io(url, {
      transports:       ['websocket', 'polling'],
      reconnection:     true,
      reconnectionDelay: 2000,
      reconnectionAttempts: 10,
      timeout:          5000,
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      setState(prev => ({ ...prev, connected: true, error: null }));
    });

    socket.on('disconnect', () => {
      setState(prev => ({ ...prev, connected: false }));
    });

    socket.on('connect_error', (err: Error) => {
      setState(prev => ({
        ...prev,
        connected: false,
        error: `خطأ في الاتصال: ${err.message}`,
      }));
    });

    socket.on('new_vote', (data: NewVoteEvent) => {
      setState(prev => ({
        ...prev,
        lastVoteTime: data.timestamp,
        voteCount:    prev.voteCount + 1,
      }));
      onNewVote?.(data);
    });

    // Keepalive ping كل 30 ثانية
    const pingInterval = setInterval(() => {
      if (socket.connected) {
        socket.emit('ping_server');
      }
    }, 30_000);

    socket.on('disconnect', () => clearInterval(pingInterval));

  }, [url, onNewVote]);

  const disconnect = useCallback(() => {
    socketRef.current?.disconnect();
    socketRef.current = null;
    setState(prev => ({ ...prev, connected: false }));
  }, []);

  useEffect(() => {
    if (autoConnect) connect();
    return () => { socketRef.current?.disconnect(); };
  }, [autoConnect, connect]);

  return { ...state, connect, disconnect, socket: socketRef.current };
}
