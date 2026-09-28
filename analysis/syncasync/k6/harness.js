// k6 harness — ReviewGate-R, read-only workload, 12 read routes + 401 probe.
//
// The mix is the read-only analogue of the archived harness: same route
// distribution shape, with every write segment removed. The 401 probe is kept
// because an unauthenticated read is part of the measured surface.
//
//   TARGET_URL   base URL              SCENARIO  steady | ramp
//   RATE         req/s, steady         WINDOW_MS measured window (default 30000)
//   WARMUP_MS    throwaway             COOLDOWN_MS ramp-down after window
//   RAMP_MAX     target for ramp       SUMMARY_FILE  JSON summary path
//
// Three window trends (warmup / window / cooldown) bucket latencies, so the
// window-only percentile is available with warmup and cooldown nonzero. Only
// the window bucket is analysed.

import http from 'k6/http';
import { check } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const TARGET = __ENV.TARGET_URL || 'http://127.0.0.1:8000';
const SCENARIO = __ENV.SCENARIO || 'steady';
const RATE = Number(__ENV.RATE || 100);
const WINDOW = Number(__ENV.WINDOW_MS || 30000);
const WARMUP = Number(__ENV.WARMUP_MS || 0);
const COOLDOWN = Number(__ENV.COOLDOWN_MS || 10000);
const RAMP_MAX = Number(__ENV.RAMP_MAX || 800);
const RAMP_MS = Number(__ENV.RAMP_MS || 8000);

// The ramp scenario must span the same three phases as the steady one, or the
// window buckets never fill. Previously it ran a single RAMP_MS stage (8 s by
// default), which is shorter than the 10 s warmup, so every sample landed in
// warmup and `window` came back null with window_requests 0 -- the knee search
// then read that as "no samples" and reported no knee at all.
//
// The ramp itself is only the discovery mechanism: it climbs to RAMP_MAX over
// RAMP_MS. The qualifying measurement is the STEADY window that follows at
// RAMP_MAX, which is what `qualifies()` scores.
export const options = SCENARIO === 'ramp'
  ? {
      scenarios: {
        ramp: {
          executor: 'ramping-arrival-rate',
          startRate: 10,
          timeUnit: '1s',
          stages: [
            { target: RAMP_MAX, duration: RAMP_MS + 'ms' },
            { target: RAMP_MAX, duration: (WARMUP + WINDOW + COOLDOWN) + 'ms' },
          ],
          preAllocatedVUs: 200,
          maxVUs: 600,
          gracefulStop: '0s',
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
          preAllocatedVUs: 200,
          maxVUs: 600,
        },
      },
      discardResponseBodies: true,
    };

const lat_warmup = new Trend('lat_window_warmup', false);
const lat_window = new Trend('lat_window_measure', false);
const lat_cooldown = new Trend('lat_window_cooldown', false);

// Counters for the measured window only. The Trend's own `count` is not reliable
// for the achieved-throughput and error-rate criteria, which need a request
// count over a known window length, so they are counted explicitly here.
const win_requests = new Counter('window_requests');
const win_errors = new Counter('window_errors');

const started = Date.now();

function inWindow() {
  const elapsed = Date.now() - started;
  return elapsed >= WARMUP && elapsed < WARMUP + WINDOW;
}

function record(dt, isError) {
  const elapsed = Date.now() - started;
  if (elapsed < WARMUP) lat_warmup.add(dt);
  else if (elapsed < WARMUP + WINDOW) lat_window.add(dt);
  else lat_cooldown.add(dt);
  if (inWindow()) {
    win_requests.add(1);
    if (isError) win_errors.add(1);
  }
}

const ADMIN = { Authorization: 'Bearer admin-token' };
const USER = { Authorization: 'Bearer user-token' };
const BAD = { Authorization: 'Bearer definitely-not-a-token' };
const EXPECT_401 = http.expectedStatuses(401);

// Read-only mix over 20 slots, mirroring the archived harness proportions with
// writes removed: 50% public read, 20% user read, 20% admin read,
// 5% bad-token 401, 5% paginated read.
const SEGMENTS = 20;

function pick() {
  const b = Math.floor(Math.random() * SEGMENTS);
  switch (b) {
    case 0:  return { path: '/health', h: null };
    case 1:  return { path: '/reviews?limit=20&offset=0', h: null };
    case 2:  return { path: '/reviews/1', h: null };
    case 3:  return { path: '/reviews/search?q=Review&limit=10', h: null };
    case 4:  return { path: '/reviews/1/comments', h: null };
    case 5:  return { path: '/reviews/stats', h: null };
    case 6:  return { path: '/reviews/2', h: null };
    case 7:  return { path: '/reviews/2/comments', h: null };
    case 8:  return { path: '/users/me', h: USER };
    case 9:  return { path: '/users/admins', h: USER };
    case 10: return { path: '/admin/dashboard', h: ADMIN };
    case 11: return { path: '/admin/config', h: ADMIN };
    case 12: return { path: '/admin/dashboard', h: ADMIN };
    case 13: return { path: '/admin/config', h: ADMIN };
    case 14: return { path: '/reviews/export', h: ADMIN };
    case 15: return { path: '/reviews/export', h: ADMIN };
    case 16: return { path: '/admin/dashboard', h: BAD };
    case 17: return { path: '/admin/dashboard', h: BAD };
    default: return { path: '/reviews?limit=5&offset=0', h: null };
  }
}

export default function () {
  const { path, h } = pick();
  const t0 = Date.now();
  const headers = Object.assign({}, h || {});
  const params = { headers };
  if (h === BAD) params.responseCallback = EXPECT_401;
  const r = http.get(TARGET + path, params);
  // an error is any response that is not the intended status; the 401 probe's
  // 401 is intended, so it is excluded by `h === BAD`
  const isError = h === BAD ? r.status !== 401 : r.status !== 200;
  record(Date.now() - t0, isError);
  check(r, {
    'status is <500': (res) => res.status < 500,
    'auth works as intended': (res) => (h === BAD ? res.status === 401 : res.status === 200),
  });
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
  const hd = data.metrics.http_req_duration;
  function counter(name) {
    const c = data.metrics[name];
    return c && c.values ? (c.values.count || 0) : 0;
  }
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
      p50: hd.values['p(50)'], p95: hd.values['p(95)'], p99: hd.values['p(99)'],
      max: hd.values.max,
    } : null,
    // window-scoped counts, used for achieved throughput and error rate
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
