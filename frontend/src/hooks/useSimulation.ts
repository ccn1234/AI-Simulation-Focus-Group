import { useState } from 'react';
import { runSimulation } from '../services/simulationApi';
import type { SimulationRequestPayload, SimulationResult } from '../types/simulation';

export function useSimulation() {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (payload: SimulationRequestPayload) => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await runSimulation(payload);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return { result, loading, error, submit };
}
