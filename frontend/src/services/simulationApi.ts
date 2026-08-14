import type { SimulationRequestPayload, SimulationResult } from '../types/simulation';
import { token } from '../components/AuthGate';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function runSimulation(payload: SimulationRequestPayload): Promise<SimulationResult> {
  const response = await fetch(`${API_BASE_URL}/simulations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token() ?? ''}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || '시뮬레이션 요청에 실패했습니다.');
  }

  return response.json();
}
