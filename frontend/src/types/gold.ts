/**
 * TypeScript Data Models for Global Gold Price Intelligence & Forecasting Platform.
 * Mapped 1:1 against FastAPI backend response schemas.
 */

export interface GoldHistoryRecord {
  date: string;
  close_usd_per_troy_oz: number;
  open_usd_per_troy_oz?: number;
  high_usd_per_troy_oz?: number;
  low_usd_per_troy_oz?: number;
  volume?: number;
  fx_usdinr?: number | null;
  gold_parity_inr_per_10g?: number | null;
  regime_name?: string;
}

export interface GoldHistoryResponse {
  status: string;
  total_returned: number;
  data: GoldHistoryRecord[];
}

export interface ForecastItem {
  model: string;
  horizon_days: number;
  forecast_origin_date: string;
  target_date_approx: string;
  current_price_usd: number;
  point_forecast_usd: number;
  lower_bound_95_usd: number;
  upper_bound_95_usd: number;
  forecast_return_pct: number;
}

export interface GoldForecastResponse {
  status: string;
  current_price_usd: number;
  forecast_date: string;
  forecast_origin_date: string;
  total_forecasts: number;
  forecasts: ForecastItem[];
}

export interface ModelMetricItem {
  model: string;
  horizon_days: number;
  mae: number;
  rmse: number;
  mape: number;
  directional_accuracy_pct: number | null;
  skill_score_pct: number | null;
  coverage_95_pct: number | null;
  avg_interval_width_usd: number | null;
  evaluation_samples: number;
}

export interface GoldMetricsResponse {
  status: string;
  evaluation_period: string;
  benchmark_baseline: string;
  models: ModelMetricItem[];
}

export interface MarketTrendAnalysis {
  latest_date: string;
  current_price_usd: number;
  current_regime: string;
  trend: {
    classification: string;
    description: string;
    sma_50d: number;
    sma_200d: number;
    sma_ratio: number;
    return_21d_pct: number;
  };
  volatility: {
    rolling_vol_30d_pct: number;
    rolling_vol_90d_pct: number;
    full_series_vol_pct: number;
  };
  drawdown: {
    all_time_high_usd: number;
    all_time_high_date: string;
    current_drawdown_pct: number;
    historical_max_drawdown_pct: number;
    historical_peak_price: number;
    historical_trough_price: number;
  };
}

export interface GoldTrendsResponse {
  status: string;
  market_analysis: MarketTrendAnalysis;
}

export interface GoldRegimeRecord {
  date: string;
  close_usd_per_troy_oz: number;
  regime: string;
  regime_conviction_score: number;
  sma_50d: number;
  sma_200d: number;
  sma_ratio: number;
  return_21d: number;
  return_63d: number;
  rolling_vol_30d: number;
  rolling_vol_90d: number;
  adx_14d: number;
  plus_di_14d: number;
  minus_di_14d: number;
  drawdown_63d_pct: number;
  regime_description: string;
}

export interface GoldRegimeHistoryResponse {
  status: string;
  total_returned: number;
  data: GoldRegimeRecord[];
}

export interface GoldIntelligenceResponse {
  status: string;
  observation_date: string;
  current_price_usd: number;
  all_time_high_usd: number;
  current_drawdown_pct: number;
  regime_intelligence: {
    regime: string;
    conviction_score: number;
    description: string;
    trend_strength_adx: number;
    sma_cross_ratio: number;
  };
  risk_profile: {
    realized_vol_30d_pct: number;
    full_series_vol_pct: number;
    var_95pct_1d: number;
    cvar_95pct_1d: number;
    historical_max_drawdown_pct: number;
  };
  scenarios_consensus_365d: {
    bullish_target_usd: number;
    base_target_usd: number;
    bearish_target_usd: number;
  };
  uncertainty_intervals_30d: {
    horizon_trading_days: number;
    point_forecast_usd: number;
    expected_return_pct: number;
    interval_50: { lower_usd: number; upper_usd: number; width_usd: number };
    interval_80: { lower_usd: number; upper_usd: number; width_usd: number };
    interval_95: { lower_usd: number; upper_usd: number; width_usd: number };
  };
  macro_signals_count: number;
}

export interface StressScenario {
  id: string;
  name: string;
  historical_analogue: string;
  shock_magnitude: string;
  gold_elasticity_beta: number;
  projected_return_pct: number;
  projected_price_usd: number;
  projected_parity_inr_per_10g?: number;
  risk_transmission: string;
  severity: string;
}

export interface GoldRiskResponse {
  status: string;
  risk_analytics: {
    latest_date: string;
    volatility: {
      realized_vol_7d_pct: number;
      realized_vol_30d_pct: number;
      realized_vol_90d_pct: number;
      full_series_vol_pct: number;
      annualized_vol_std_daily_pct: number;
    };
    drawdowns: {
      current_price_usd: number;
      all_time_high_usd: number;
      all_time_high_date: string;
      current_drawdown_pct: number;
      days_since_ath: number;
      trading_days_since_ath: number;
      historical_max_drawdown_pct: number;
      historical_peak_price_usd: number;
      historical_peak_date: string;
      historical_trough_price_usd: number;
      historical_trough_date: string;
      historical_recovery_date: string | null;
      historical_recovery_trading_days: number | null;
      historical_recovery_calendar_days: number | null;
      historical_recovery_status: string;
    };
    value_at_risk: {
      methodology: string;
      observations_evaluated: number;
      metrics: {
        var_95pct_1d: number;
        cvar_95pct_1d: number;
        var_99pct_1d: number;
        cvar_99pct_1d: number;
        var_95pct_10d: number;
        var_99pct_10d: number;
      };
      explanations: Record<string, string>;
    };
    stress_testing: {
      methodology: string;
      scenarios: StressScenario[];
    };
  };
}

export interface HorizonProjection {
  horizon_trading_days: number;
  target_calendar_date_approx: string;
  target_price_usd: number;
  projected_return_pct: number;
  lower_range_usd: number;
  upper_range_usd: number;
}

export interface ScenarioDetail {
  name: string;
  macro_thesis: string;
  macro_assumptions: Record<string, string>;
  risk_factors: string[];
  horizon_projections: HorizonProjection[];
  price_trajectory: Array<{ date: string; price: number; day: number }>;
}

export interface GoldScenariosResponse {
  status: string;
  scenario_forecasts: {
    methodology: string;
    audit_disclaimer: string;
    forecast_origin_date: string;
    base_spot_price_usd: number;
    scenarios: {
      bullish: ScenarioDetail;
      base: ScenarioDetail;
      bearish: ScenarioDetail;
    };
  };
}

export interface UncertaintyHorizonEvaluation {
  horizon_trading_days: number;
  evaluation_samples: number;
  uncalibrated_gaussian_95_cov_pct: number;
  uncalibrated_gaussian_95_width_usd: number;
  conformal_50_cov_pct: number;
  conformal_50_width_usd: number;
  conformal_80_cov_pct: number;
  conformal_80_width_usd: number;
  conformal_95_cov_pct: number;
  conformal_95_width_usd: number;
  conformal_95_upper_breaches: number;
  conformal_95_lower_breaches: number;
  latest_60d_rolling_coverage_pct: number;
  calibration_diagnosis: string;
}

export interface GoldUncertaintyResponse {
  status: string;
  uncertainty_engine: {
    forecast_origin_date: string;
    current_price_usd: number;
    conformal_multipliers: Record<string, Record<string, number>>;
    test_uncertainty_audit: {
      methodology: string;
      validation_period: string;
      test_evaluation_period: string;
      horizon_evaluations: UncertaintyHorizonEvaluation[];
    };
    production_intervals: Array<{
      horizon_trading_days: number;
      point_forecast_usd: number;
      expected_return_pct: number;
      interval_50: { lower_usd: number; upper_usd: number; width_usd: number };
      interval_80: { lower_usd: number; upper_usd: number; width_usd: number };
      interval_95: { lower_usd: number; upper_usd: number; width_usd: number };
    }>;
  };
}

export interface MacroIndicatorDetail {
  name: string;
  provider: string;
  frequency: string;
  unit: string;
  observation_cadence: string;
  publication_lag: string;
  missing_value_handling: string;
  revision_policy: string;
  licensing: string;
  point_in_time_available: boolean;
  latest_reference_value: number;
  status: string;
}

export interface GoldMacroResponse {
  status: string;
  governance_guarantee: string;
  total_indicators_tracked: number;
  indicators: Record<string, MacroIndicatorDetail>;
}
