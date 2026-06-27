// netlify/functions/_ratelimit.js
// Cost guard for paid agent endpoints. Pure in-memory, ZERO dependencies.
// Global daily cap + per-IP per-minute throttle. Counters reset on cold start
// (caps casual/burst abuse; durable store is a later upgrade).
const DAILY_CAP  = parseInt(process.env.FC_AGENT_DAILY_CAP  || '100', 10);
const IP_PER_MIN = parseInt(process.env.FC_AGENT_IP_PER_MIN || '5',   10);
const mem = { day: '', dayCount: 0, ip: {} };
function today()  { return new Date().toISOString().slice(0, 10); }
function minute() { return Math.floor(Date.now() / 60000); }
async function checkAndCount(ip) {
  if (mem.day !== today()) { mem.day = today(); mem.dayCount = 0; mem.ip = {}; }
  if (mem.dayCount >= DAILY_CAP) return { ok: false, status: 429, reason: 'daily_cap' };
  const ipKey = (ip || 'unknown') + ':' + minute();
  const c = mem.ip[ipKey] || 0;
  if (c >= IP_PER_MIN) return { ok: false, status: 429, reason: 'ip_throttle' };
  if (Math.random() < 0.02) { const m = minute(); for (const k in mem.ip) { if (parseInt(k.split(':').pop(),10) < m) delete mem.ip[k]; } }
  mem.ip[ipKey] = c + 1; mem.dayCount += 1;
  return { ok: true };
}
function clientIp(event) {
  const h = (event && event.headers) || {};
  return (h['x-nf-client-connection-ip'] || h['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
}
module.exports = { checkAndCount, clientIp, DAILY_CAP, IP_PER_MIN };
