import type {
  SimulationJobResponse,
  SimulationRequestPayload,
  SimulationStatusResponse,
} from '../types/simulation';
import { token } from '../components/AuthGate';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

function authHeaders(): HeadersInit {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token() ?? ''}`,
  };
}

async function apiError(response: Response): Promise<Error> {
  const contentType = response.headers.get('content-type') ?? '';

  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === 'string' && body.detail.trim()) {
        return new Error(body.detail);
      }
    } catch {
      // Use the status-based message below when invalid JSON is returned.
    }
  }

  const status = `${response.status} ${response.statusText}`.trim();
  return new Error(`API 요청에 실패했습니다. (${status})`);
}

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw await apiError(response);
  }

  const contentType = response.headers.get('content-type') ?? '';
  if (!contentType.includes('application/json')) {
    throw new Error(`서버가 JSON이 아닌 응답을 반환했습니다. (${response.status})`);
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new Error('서버가 올바르지 않은 JSON 응답을 반환했습니다.');
  }
}

export async function createSimulationJob(
  payload: SimulationRequestPayload,
  signal?: AbortSignal,
): Promise<SimulationJobResponse> {
  const response = await fetch(`${API_BASE_URL}/simulations`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
    signal,
  });

  return readJson<SimulationJobResponse>(response);
}

export async function getSimulationStatus(
  simulationId: number,
  signal?: AbortSignal,
): Promise<SimulationStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}`, {
    method: 'GET',
    headers: authHeaders(),
    cache: 'no-store',
    signal,
  });

  return readJson<SimulationStatusResponse>(response);
}
