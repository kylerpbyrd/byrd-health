import { useEffect, useRef, useState, useCallback } from "react";

export interface DeviceReading {
  type: "device_reading";
  payload: {
    profile_slug: string;
    timestamp: string;
    data: {
      device_id: string;
      device_type: string;
      temperature: number;
    };
  };
}

export interface AnalysisComplete {
  type: "analysis_complete";
  payload: { profile_slug: string; timestamp: string; data: Record<string, unknown> };
}

export type WSMessage = DeviceReading | AnalysisComplete;

interface UseWebSocketOptions {
  onDeviceReading?: (reading: DeviceReading) => void;
  onAnalysisComplete?: (msg: AnalysisComplete) => void;
}

function getWebSocketUrl(): string {
  const ingress = (window as unknown as { __INGRESS_PATH__?: string }).__INGRESS_PATH__ || "";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${protocol}//${host}${ingress}/api/v1/fertility/ws`;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  // DEBUG: Kill switch until POST debugging is complete.
  // Set window.__ENABLE_WS__ = true in the browser console to re-enable.
  if (!(window as unknown as { __ENABLE_WS__?: boolean }).__ENABLE_WS__) {
    return { isConnected: false, lastMessage: null };
  }

  const { onDeviceReading, onAnalysisComplete } = options;
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);

  const optionsRef = useRef(options);
  optionsRef.current = options;

  const reconnectDelayRef = useRef(1000);
  const wsRef = useRef<WebSocket | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    const url = getWebSocketUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) {
        ws.close();
        return;
      }
      setIsConnected(true);
      reconnectDelayRef.current = 1000;
    };

    ws.onmessage = (event: MessageEvent) => {
      if (!mountedRef.current) return;
      try {
        const msg: WSMessage = JSON.parse(event.data as string);
        setLastMessage(msg);

        if (msg.type === "device_reading" && onDeviceReading) {
          onDeviceReading(msg);
        }
        if (msg.type === "analysis_complete" && onAnalysisComplete) {
          onAnalysisComplete(msg);
        }
      } catch {
        // Ignore unparseable messages
      }
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      setIsConnected(false);
      wsRef.current = null;

      const delay = reconnectDelayRef.current;
      reconnectDelayRef.current = Math.min(delay * 2, 30000);

      setTimeout(() => {
        if (mountedRef.current) {
          connect();
        }
      }, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onDeviceReading, onAnalysisComplete]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return { isConnected, lastMessage };
}
