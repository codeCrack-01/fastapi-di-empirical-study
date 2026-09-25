// k6 harness.js — shared load generator for ReviewGate S0-S3.
//
// Config via env (see run_experiment.py for how it's invoked):
//   TARGET_URL      base URL, e.g. http://127.0.0.1:8000
//   SCENARIO        steady | ramp
//   RATE            constant arrival rate in req/s (steady only)
//   DURATION_MS     steady window duration in ms (default 30000)
//   WARMUP_MS       throwaway warm-up time in ms (default 0)
//   COOLDOWN_MS     ramp-down to zero after the window (steady only)
//   RAMP_MAX_RPS    target rate for the ramp scenario (default 800)
//
// Window-isolated stats come from data.metrics.<trend> in handleSummary; the
// per-request CSV is sliced by timestamp in analyze.py.
//
// Run: k6 run harness.js

import http from 'k6/http';
import { check } from 'k6';
import { Trend } from 'k6/metrics';

const TARGET = __ENV.TARGET_URL || 'http://127.0.0.1:8000';
const SCENARIO = __ENV.SCENARIO || 'steady';
const RATE = Number(__ENV.RATE || 100);
const WINDOW = Number(__ENV.DURATION_MS || 30000);
const WARMUP = Number(__ENV.WARMUP_MS || 0);
const COOLDOWN = Number(__ENV.COOLDOWN_MS || 10000);
const RAMP_MAX = Number(__ENV.RAMP_MAX_RPS || 800);

export const options = SCENARIO === 'ramp'
  ? {
      scenarios: {
        ramp: {
          executor: 'ramping-arrival-rate',
          startRate: 1,
          timeUnit: '1s',
          stages: [{ target: RAMP_MAX, duration: '300s' }],
          preAllocatedVUs: 500,
          maxVUs: 1000,
        },
      },
      discardResponseBodies: true,
    }
  : {
      scenarios: {
        steady: {
          executor: 'constant-arrival-rate',
          rate: RATE,
          timeUnit: '1s',
          duration: (WARMUP + WINDOW + COOLDOWN) + 'ms',
          preAllocatedVUs: 500,
          maxVUs: 1000,
        },
      },
      discardResponseBodies: true,
    };

// Three window trends (warmup / window / cooldown) bucket latencies, so the
// window-only percentile is available even when warmup+cooldown are nonzero.
const lat_warmup = new Trend('lat_window_warmup', false);
const lat_window = new Trend('lat_window_measure', false);
const lat_cooldown = new Trend('lat_window_cooldown', false);

const started = Date.now();

function record(dt) {
  const elapsed = Date.now() - started;
  if (elapsed < WARMUP) lat_warmup.add(dt);
  else if (elapsed < WARMUP + WINDOW) lat_window.add(dt);
  else lat_cooldown.add(dt);
}

const ADMIN = { Authorization: 'Bearer admin-token' };
const EDITOR = { Authorization: 'Bearer editor-token' };
const USER = { Authorization: 'Bearer user-token' };
const BAD = { Authorization: 'Bearer definitely-not-a-token' };

// Workload mix (all bodies/auth valid) matching the route table shape:
// ~10% health, ~20% public read, ~20% authed read, ~10% export (needs admin),
// ~15% create, ~10% vote, ~10% flag, ~5% bad-token 401, ~9% detail reads.
const SEGMENTS = 20;

function pick() {
  const b = Math.floor(Math.random() * SEGMENTS);
  switch (b) {
    case 0:  return { m: 'get', path: '/health', h: null };
    case 1:  return { m: 'get', path: '/reviews?limit=20&offset=0', h: null };
    case 2:  return { m: 'get', path: '/reviews/1', h: null };
    case 3:  return { m: 'get', path: '/reviews/search?q=Review&limit=10', h: null };
    case 4:  return { m: 'get', path: '/reviews/1/comments', h: null };
    case 5:  return { m: 'get', path: '/users/me', h: USER };
    case 6:  return { m: 'get', path: '/users/admins', h: USER };
    case 7:  return { m: 'get', path: '/admin/dashboard', h: ADMIN };
    case 8:  return { m: 'get', path: '/admin/config', h: ADMIN };
    case 9:  return { m: 'get', path: '/reviews/export', h: ADMIN };
    case 10: return { m: 'post', path: '/reviews', h: EDITOR, body: JSON.stringify({ title: 'Perf', body: 'Body', rating: 4 }) };
    case 11: return { m: 'post', path: '/reviews', h: EDITOR, body: JSON.stringify({ title: 'Perf', body: 'Body', rating: 4 }) };
    case 12: return { m: 'post', path: '/reviews', h: EDITOR, body: JSON.stringify({ title: 'Perf', body: 'Body', rating: 4 }) };
    case 13: return { m: 'post', path: '/reviews/2/votes', h: USER, body: JSON.stringify({ value: 1 }) };
    case 14: return { m: 'post', path: '/reviews/2/votes', h: USER, body: JSON.stringify({ value: 1 }) };
    case 15: return { m: 'post', path: '/reviews/1/flag', h: EDITOR, body: JSON.stringify({}) };
    case 16: return { m: 'post', path: '/reviews/1/flag', h: EDITOR, body: JSON.stringify({}) };
    case 17: return { m: 'post', path: '/reviews/1/approve', h: ADMIN, body: JSON.stringify({}) };
    case 18: return { m: 'get', path: '/admin/dashboard', h: BAD };   // 401 exercised
    default: return { m: 'get', path: '/reviews?limit=5&offset=0', h: null };
  }
}

export default function () {
  const { m, path, h, body } = pick();
  const t0 = Date.now();
  let r;
  const headers = Object.assign({}, h || {});
  if (body) headers['Content-Type'] = 'application/json';
  const params = { headers };
  if (m === 'get') r = http.get(TARGET + path, params);
  else if (body) r = http.post(TARGET + path, body, params);
  else r = http.post(TARGET + path, null, params);
  record(Date.now() - t0);
  check(r, {
    'status is <500': (res) => res.status < 500,
    'auth works as intended': (res) => {
      if (h === BAD) return res.status === 401;
      return res.status === 200;
    },
  });
}

export function handleSummary(data) {
  function trend(name) {
    const t = data.metrics[name];
    if (!t || !t.values) return null;
    return { count: t.values.count, p50: t.values.med, p95: t.values['p(95)'],
             p99: t.values['p(99)'], mean: t.values.avg, min: t.values.min, max: t.values.max };
  }
  const hd = data.metrics.http_req_duration;
  const summary = {
    scenario: SCENARIO,
    target: TARGET,
    rate: RATE,
    window_ms: WINDOW,
    warmup_ms: WARMUP,
    window: trend('lat_window_measure'),
    warmup: trend('lat_window_warmup'),
    cooldown: trend('lat_window_cooldown'),
    http_req_duration: hd ? {
      count: hd.values.count, avg: hd.values.avg,
      p50: hd.values['p(50)'], p95: hd.values['p(95)'], p99: hd.values['p(99)'], max: hd.values.max,
    } : null,
    checkFailures: data.metrics.checks ? data.metrics.checks.values.fails : null,
    httpErrors: data.metrics.http_req_failed ? data.metrics.http_req_failed.values.rate : null,
  };
  const path = __ENV.SUMMARY_FILE || '';
  const out = {};
  if (path) out[path] = JSON.stringify(summary);
  out['stdout'] = JSON.stringify(summary);
  return out;
}