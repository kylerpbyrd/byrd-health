import { useEffect, useRef, useState, useCallback } from "react";

export interface WSEnvelope {
  version: number;
  type: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

export interface DeviceReadingPayload {
  profile_slug: string;
  device_id: string;
  device_type: string;
  temperature: number;
}

export interface AnalysisCompletePayload {
  profile_slug: string;
}

interface UseWebSocketOptions {
  onDeviceReading?: (reading: DeviceReadingPayload) => void;
  onAnalysisComplete?: (msg: AnalysisCompletePayload) => void;
}

function getWebSocketUrl(): string {
  const ingress = (window as unknown as { __INGRESS_PATH__?: string }).__INGRESS_PATH__ || "";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${protocol}//${host}${ingress}/api/v1/fertility/ws`;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { onDeviceReading, onAnalysisComplete } = options;
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSEnvelope | null>(null);

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
      console.log("WebSocket opened, setting isConnected=true");
      setIsConnected(true);
      reconnectDelayRef.current = 1000;
    };

    ws.onmessage = (event: MessageEvent) => {
      if (!mountedRef.current) return;
      const { onDeviceReading: onDR, onAnalysisComplete: onAC } = optionsRef.current;
      try {
        const msg: WSEnvelope = JSON.parse(event.data as string);
        if (msg.version !== 1) {
          console.warn("Unsupported WebSocket protocol version:", msg.version);
          return;
        }
        setLastMessage(msg);

        if (msg.type === "device_reading" && onDR) {
          onDR(msg.payload as unknown as DeviceReadingPayload);
        }
        if (msg.type === "analysis_complete" && onAC) {
          onAC(msg.payload as unknown as AnalysisCompletePayload);
        }
      } catch {
        // Ignore unparseable messages
      }
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      console.log("WebSocket closed, setting isConnected=false");
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
  }, []);

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
