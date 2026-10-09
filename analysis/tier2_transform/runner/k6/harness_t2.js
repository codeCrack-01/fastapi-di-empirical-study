// k6 open-loop harness for tier-2 (real-repo) arms.
//
// Mirror of the tier-1 syncasync harness: same executor (constant-arrival-rate,
// OPEN LOOP: offered rate is fired regardless of completion), same windowing
// (warmup / measured window / cooldown), same primary metric (lat_cell: every
// request in the cell, no window attribution), same offered-vs-achieved
// accounting (load_fidelity + dropped_iterations hypertension guard) and same
// per-window error counter. Only the workload differs: tier-2 fires a single
// representative GET route per app instead of the 12-route ReviewGate-R mix.
//
//   TARGET_URL     base URL, e.g. http://127.0.0.1:8701
//   TARGET_PATH    single route to measure, e.g. /api/auth/me
//   RATE           offered req/s (constant-arrival-rate)
//   WINDOW_MS      measured window (default 30000)
//   WARMUP_MS      throwaway (default 10000)
//   COOLDOWN_MS    ramp-down (default 10000)
//   REQ_TIMEOUT_MS per-request timeout (default 5000) -- a timeout here is a
//                  saturation signal, not an artefact (same as tier-1)
//   AUTH_HEADER    header name carrying the token (default "Authorization")
//   AUTH_BEARER    full header VALUE (e.g. "Bearer <jwt>" or a raw service
//                  token), sent only if set

import http from 'k6/http';
import { check } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const TARGET = __ENV.TARGET_URL || 'http://127.0.0.1:8000';
const PATH = __ENV.TARGET_PATH || '/';
const RATE = Number(__ENV.RATE || 100);
const WINDOW = Number(__ENV.WINDOW_MS || 30000);
const WARMUP = Number(__ENV.WARMUP_MS || 10000);
const COOLDOWN = Number(__ENV.COOLDOWN_MS || 10000);
const REQ_TIMEOUT = Number(__ENV.REQ_TIMEOUT_MS || 5000);
const AUTH_HEADER = __ENV.AUTH_HEADER || 'Authorization';
const AUTH = __ENV.AUTH_BEARER || '';

const SUMMARY_TREND_STATS = ['avg', 'min', 'med', 'max', 'p(50)', 'p(90)', 'p(95)', 'p(99)'];

export const options = {
  scenarios: {
    steady: {
      executor: 'constant-arrival-rate',
      rate: RATE,
      timeUnit: '1s',
      duration: (WARMUP + WINDOW + COOLDOWN) + 'ms',
      preAllocatedVUs: 200,
      maxVUs: 600,
    },
  },
  summaryTrendStats: SUMMARY_TREND_STATS,
  discardResponseBodies: true,
};

const lat_cell = new Trend('lat_cell', false);
const lat_window_measure = new Trend('lat_window_measure', false);
const win_requests = new Counter('window_requests');
const win_errors = new Counter('window_errors');
const cell_samples = new Counter('cell_samples');
const http_samples = new Counter('http_samples');

const started = Date.now();

function inWindow() {
  const elapsed = Date.now() - started;
  return elapsed >= WARMUP && elapsed < WARMUP + WINDOW;
}

function record(dt, isError) {
  lat_cell.add(dt);
  cell_samples.add(1);
  http_samples.add(1);
  if (inWindow()) {
    lat_window_measure.add(dt);
    win_requests.add(1);
    if (isError) win_errors.add(1);
  }
}

export default function () {
  const t0 = Date.now();
  const headers = {};
  if (AUTH) headers[AUTH_HEADER] = AUTH;
  const r = http.get(TARGET + PATH, { headers, timeout: REQ_TIMEOUT + 'ms' });
  record(Date.now() - t0, r.status >= 400);
  check(r, { 'status < 400': (res) => res.status < 400 });
}

export function handleSummary(data) {
  function trend(name) {
    const t = data.metrics[name];
    if (!t || !t.values) return null;
    return {
      count: t.values.count,
      p50: t.values.med,
      p95: t.values['p(95)'],
      p99: t.values['p(99)'],
      mean: t.values.avg,
      min: t.values.min,
      max: t.values.max,
    };
  }
  function counter(name) {
    const c = data.metrics[name];
    return c && c.values ? (c.values.count || 0) : 0;
  }
  const dropped = counter('dropped_iterations');
  const offered = RATE * (WINDOW / 1000);
  const achieved = counter('window_requests');
  const load_fidelity = offered > 0 ? achieved / offered : null;

  const hd = data.metrics.http_req_duration;
  const summary = {
    target: TARGET + PATH,
    rate: RATE,
    window_ms: WINDOW,
    warmup_ms: WARMUP,
    cell: Object.assign(trend('lat_cell'), { count: counter('cell_samples') }),
    window: trend('lat_window_measure') || null,
    http_req_duration: hd ? {
      count: counter('http_samples'), avg: hd.values.avg,
      p50: hd.values['p(50)'], p95: hd.values['p(95)'], p99: hd.values['p(99)'],
      max: hd.values.max,
    } : null,
    offered_rate: RATE,
    offered_requests: offered,
    achieved_rate: achieved / (WINDOW / 1000),
    load_fidelity: load_fidelity,
    dropped_iterations: dropped,
    window_requests: counter('window_requests'),
    window_errors: counter('window_errors'),
    iterations: data.metrics.iterations ? data.metrics.iterations.values.count : null,
    checkFailures: data.metrics.checks ? data.metrics.checks.values.fails : null,
    checks: data.metrics.checks ? data.metrics.checks.values.passes : null,
    httpErrors: data.metrics.http_req_failed ? data.metrics.http_req_failed.values.rate : null,
  };
  const path = __ENV.SUMMARY_FILE || '';
  const out = {};
  if (path) out[path] = JSON.stringify(summary);
  out['stdout'] = JSON.stringify(summary);
  return out;
}