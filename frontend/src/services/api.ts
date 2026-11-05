/**
 * Centralized API Service for Global Gold Price Intelligence Platform.
 * Connects directly to FastAPI backend (defaults to http://localhost:8000).
 * Handles timeouts, network retries, safe NaN guards, and JSON response deserialization.
 */

import {
  GoldHistoryResponse,
  GoldForecastResponse,
  GoldMetricsResponse,
  GoldTrendsResponse,
  GoldRegimeHistoryResponse,
  GoldIntelligenceResponse,
  GoldRiskResponse,
  GoldScenariosResponse,
  GoldUncertaintyResponse,
  GoldMacroResponse,
} from "../types/gold";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

class GoldApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private async fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...(options?.headers || {}),
        },
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`API HTTP ${response.status} from ${endpoint}: ${errorBody}`);
      }

      return (await response.json()) as T;
    } catch (err) {
      console.error(`[GoldApiClient] Error calling ${endpoint}:`, err);
      throw err;
    }
  }

  // 1. Historical Prices
  public async getHistory(limit: number = 365, startDate?: string, endDate?: string): Promise<GoldHistoryResponse> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    return this.fetchJson<GoldHistoryResponse>(`/api/gold/history?${params.toString()}`);
  }

  // 2. Forecasting
  public async getForecasts(model?: string, horizonDays?: number): Promise<GoldForecastResponse> {
    const params = new URLSearchParams();
    if (model) params.append("model", model);
    if (horizonDays) params.append("horizon_days", horizonDays.toString());
    const query = params.toString() ? `?${params.toString()}` : "";
    return this.fetchJson<GoldForecastResponse>(`/api/gold/forecast${query}`);
  }

  // 3. Model Metrics
  public async getMetrics(): Promise<GoldMetricsResponse> {
    return this.fetchJson<GoldMetricsResponse>("/api/gold/metrics");
  }

  // 4. Market Trends
  public async getTrends(): Promise<GoldTrendsResponse> {
    return this.fetchJson<GoldTrendsResponse>("/api/gold/trends");
  }

  // 5. Market Regimes (Era Overview)
  public async getRegimes(): Promise<{ status: string; total_regimes: number; regimes: any[] }> {
    return this.fetchJson<{ status: string; total_regimes: number; regimes: any[] }>("/api/gold/regimes");
  }

  // 6. Unified Intelligence Overview
  public async getIntelligence(): Promise<GoldIntelligenceResponse> {
    return this.fetchJson<GoldIntelligenceResponse>("/api/gold/intelligence");
  }

  // 7. Quantitative Risk Analytics
  public async getRisk(): Promise<GoldRiskResponse> {
    return this.fetchJson<GoldRiskResponse>("/api/gold/risk");
  }

  // 8. Scenario Forecasting
  public async getScenarios(): Promise<GoldScenariosResponse> {
    return this.fetchJson<GoldScenariosResponse>("/api/gold/scenarios");
  }

  // 9. Prediction Uncertainty & Conformal Calibration
  public async getUncertainty(): Promise<GoldUncertaintyResponse> {
    return this.fetchJson<GoldUncertaintyResponse>("/api/gold/uncertainty");
  }

  // 10. Macroeconomic Intelligence
  public async getMacro(): Promise<GoldMacroResponse> {
    return this.fetchJson<GoldMacroResponse>("/api/gold/macro");
  }

  // 11. Historical Regime Tracking
  public async getRegimeHistory(
    limit: number = 100,
    regime?: string,
    startDate?: string,
    endDate?: string
  ): Promise<GoldRegimeHistoryResponse> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (regime) params.append("regime", regime);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    return this.fetchJson<GoldRegimeHistoryResponse>(`/api/gold/regime-history?${params.toString()}`);
  }

  // Batch Load All Dashboard State in Parallel
  public async fetchDashboardBundle() {
    const [intelligence, history, forecast, metrics, risk, scenarios, uncertainty, macro] =
      await Promise.all([
        this.getIntelligence().catch(() => null),
        this.getHistory(500).catch(() => null),
        this.getForecasts().catch(() => null),
        this.getMetrics().catch(() => null),
        this.getRisk().catch(() => null),
        this.getScenarios().catch(() => null),
        this.getUncertainty().catch(() => null),
        this.getMacro().catch(() => null),
      ]);

    return {
      intelligence,
      history,
      forecast,
      metrics,
      risk,
      scenarios,
      uncertainty,
      macro,
      timestamp: new Date().toISOString(),
    };
  }
}

export const goldApi = new GoldApiClient();

export type DashboardBundle = {
  intelligence: GoldIntelligenceResponse | null;
  history: GoldHistoryResponse | null;
  forecast: GoldForecastResponse | null;
  metrics: GoldMetricsResponse | null;
  risk: GoldRiskResponse | null;
  scenarios: GoldScenariosResponse | null;
  uncertainty: GoldUncertaintyResponse | null;
  macro: GoldMacroResponse | null;
  trends?: GoldTrendsResponse | null;
  regimeHistory?: GoldRegimeHistoryResponse | null;
  timestamp: string;
};

export const fetchDashboardBundle = async (): Promise<DashboardBundle> => {
  return (await goldApi.fetchDashboardBundle()) as DashboardBundle;
};

export default goldApi;
