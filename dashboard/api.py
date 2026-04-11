#!/usr/bin/env python3
"""Simple API to serve BLAI data to the dashboard."""
import json, os, glob, time, secrets, urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

MEMORY_DIR = Path('/home/tonny/blai-v2/memory')
CONFIG_DIR = Path('/home/tonny/blai-v2/config')
BRIDGE_DIR = Path('/home/tonny/blai-v2/claude-bridge')

# Load token at startup so misconfig fails loudly
try:
    DASHBOARD_TOKEN = json.loads((CONFIG_DIR / 'api_keys.json').read_text()).get('dashboard_token', '')
except Exception:
    DASHBOARD_TOKEN = ''
if not DASHBOARD_TOKEN or len(DASHBOARD_TOKEN) < 24:
    raise SystemExit('ERROR: dashboard_token missing or too short in api_keys.json')

# Paths that bypass auth (must NOT leak any sensitive data)
PUBLIC_PATHS = {'/favicon.ico', '/robots.txt', '/healthz', '/api/ping'}

# Audit log for unauthorized hits
AUDIT_LOG = Path('/home/tonny/blai-v2/memory/dashboard_audit.log')

# Per-IP brute force tracking: ip -> (failed_count, first_fail_ts, blocked_until_ts)
BRUTE_FORCE_TRACK = {}
BLOCK_THRESHOLD = 10            # 5 failed attempts
BLOCK_WINDOW_S  = 60           # within 60 seconds
BLOCK_DURATION_S = 300         # blocks for 10 minutes



class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='/home/tonny/blai-v2/dashboard', **kwargs)

    def _client_ip(self):
        # Honor X-Forwarded-For only if behind a trusted proxy (we are not)
        return self.client_address[0] if self.client_address else 'unknown'

    def _audit(self, reason, path):
        try:
            # SECURITY: never log tokens in plaintext, even partial. Redact entire query string.
            safe_path = path.split('?', 1)[0] + '?[REDACTED]' if '?' in path else path
            with open(AUDIT_LOG, 'a') as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + self._client_ip() + ' ' + reason + ' ' + safe_path + '\n')
        except Exception:
            pass

    def _is_blocked(self):
        ip = self._client_ip()
        rec = BRUTE_FORCE_TRACK.get(ip)
        if not rec:
            return False
        failed, first_ts, blocked_until = rec
        if blocked_until and time.time() < blocked_until:
            return True
        return False

    def _record_fail(self):
        ip = self._client_ip()
        now = time.time()
        rec = BRUTE_FORCE_TRACK.get(ip, (0, now, 0))
        failed, first_ts, blocked_until = rec
        # Reset window if first failure was long ago
        if now - first_ts > BLOCK_WINDOW_S:
            failed = 0
            first_ts = now
        failed += 1
        if failed >= BLOCK_THRESHOLD:
            blocked_until = now + BLOCK_DURATION_S
            self._audit('BLOCKED_BRUTE_FORCE_' + str(failed) + '_attempts', self.path)
        BRUTE_FORCE_TRACK[ip] = (failed, first_ts, blocked_until)

    def _record_success(self):
        # Clear tracking on successful auth
        ip = self._client_ip()
        if ip in BRUTE_FORCE_TRACK:
            del BRUTE_FORCE_TRACK[ip]

    def _is_authorized(self):
        # 0. Block if currently rate-limited (no double-record)
        if self._is_blocked():
            return False
        # If a successful auth comes in for the same IP that just got blocked,
        # the block was a false positive — caller already passes self.headers,
        # so we still verify the token first below
        # 1. Public paths bypass
        path_only = self.path.split('?')[0]
        if path_only in PUBLIC_PATHS:
            return True
        # 2. Bearer header
        h = self.headers.get('Authorization', '')
        if h.startswith('Bearer ') and secrets.compare_digest(h[7:].strip(), DASHBOARD_TOKEN):
            self._record_success()
            return True
        # 3. ?token= query param
        try:
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            tok = (params.get('token') or [''])[0]
            if tok and secrets.compare_digest(tok, DASHBOARD_TOKEN):
                self._record_success()
                return True
        except Exception:
            pass
        # Failed auth — record for brute force tracking
        self._record_fail()
        return False

    def _send_401(self):
        if self._is_blocked():
            self.send_response(429)
            self.send_header('Retry-After', str(BLOCK_DURATION_S))
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"too_many_attempts","retry_after_s":' + str(BLOCK_DURATION_S).encode() + b'}')
            return
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Bearer realm="BLAI dashboard"')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"error":"unauthorized","hint":"append ?token=YOUR_TOKEN or send Authorization: Bearer header"}')



    def do_GET(self):
        if not self._is_authorized():
            self._audit('UNAUTHORIZED', self.path)
            self._send_401()
            return
        # Strip ?token=... from path so static file serving works
        if '?' in self.path:
            self.path = self.path.split('?')[0]
        if self.path == '/api/status':
            self.send_json(self.get_status())
        elif self.path == '/api/stats':
            self.send_json(self.get_stats())
        elif self.path == '/api/conversations':
            self.send_json(self.get_conversations())
        elif self.path == '/api/people':
            self.send_json(self.get_people())
        elif self.path == '/api/actions':
            self.send_json(self.get_actions())
        else:
            super().do_GET()

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


    def get_status(self):
        """Server-side health check for Gemini, Groq, Make.com, WhatsApp.
        Returns counts + redacted key suffixes only — NEVER raw keys."""
        import urllib.request as _ur, urllib.error as _ue
        import requests as _rq
        result = {
            'ts': int(time.time()),
            'gemini': {'model': 'gemini-2.5-flash-lite', 'total': 0, 'active': 0, 'keys': []},
            'groq':   {'model': 'llama-3.3-70b-versatile', 'total': 0, 'active': 0, 'keys': []},
            'make_com': {'ok': False, 'scenarios_total': 0, 'scenarios_active': 0, 'scenarios_invalid': 0},
            'whatsapp': {'connected': False, 'uptime_s': 0},
            'brain_state': {},
        }
        # ---------- Gemini ----------
        try:
            keys = json.loads((CONFIG_DIR / 'api_keys.json').read_text()).get('gemini', [])
            if isinstance(keys, str):
                keys = [keys]
            result['gemini']['total'] = len(keys)
            body = json.dumps({'contents':[{'parts':[{'text':'hi'}]}],'generationConfig':{'maxOutputTokens':5}}).encode()
            for i, k in enumerate(keys, 1):
                status = 'ERROR'
                code = 0
                try:
                    req = _ur.Request(
                        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=' + k,
                        data=body, headers={'Content-Type': 'application/json'}
                    )
                    r = _ur.urlopen(req, timeout=8)
                    code = r.status
                    status = 'READY'
                    result['gemini']['active'] += 1
                except _ue.HTTPError as e:
                    code = e.code
                    status = 'QUOTA_EXCEEDED' if e.code == 429 else 'ERROR_' + str(e.code)
                except Exception:
                    status = 'NETWORK_ERROR'
                result['gemini']['keys'].append({'n': i, 'suffix': k[-4:], 'status': status, 'http': code})
        except Exception as e:
            result['gemini']['error'] = str(e)
        # ---------- Groq ----------
        try:
            keys = json.loads((CONFIG_DIR / 'api_keys.json').read_text()).get('groq', [])
            if isinstance(keys, str):
                keys = [keys]
            result['groq']['total'] = len(keys)
            for i, k in enumerate(keys, 1):
                status = 'ERROR'
                code = 0
                try:
                    r = _rq.post(
                        'https://api.groq.com/openai/v1/chat/completions',
                        headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json'},
                        json={'model': 'llama-3.3-70b-versatile', 'messages':[{'role':'user','content':'hi'}], 'max_tokens': 5},
                        timeout=8,
                    )
                    code = r.status_code
                    if code == 200:
                        status = 'READY'
                        result['groq']['active'] += 1
                    elif code == 429:
                        status = 'QUOTA_EXCEEDED'
                    else:
                        status = 'ERROR_' + str(code)
                except Exception:
                    status = 'NETWORK_ERROR'
                result['groq']['keys'].append({'n': i, 'suffix': k[-4:], 'status': status, 'http': code})
        except Exception as e:
            result['groq']['error'] = str(e)
        # ---------- Make.com ----------
        try:
            import sys as _sys
            _sys.path.insert(0, '/home/tonny/blai-v2')
            from skills.make_com import health_snapshot as _hs
            snap = _hs()
            result['make_com']['ok'] = snap.get('ok', False)
            result['make_com']['scenarios_total'] = snap.get('total', 0)
            result['make_com']['scenarios_active'] = snap.get('active', 0)
            result['make_com']['scenarios_invalid'] = snap.get('invalid', 0)
        except Exception as e:
            result['make_com']['error'] = str(e)
        # ---------- WhatsApp ----------
        try:
            h = MEMORY_DIR.parent / '.health'
            if h.exists():
                d = json.loads(h.read_text())
                result['whatsapp']['connected'] = d.get('status') in ('alive', 'ready')
                result['whatsapp']['uptime_s'] = int(d.get('uptime', 0))
        except Exception:
            pass
        # ---------- Brain state ----------
        try:
            bs = CONFIG_DIR / 'brain_state.json'
            if bs.exists():
                result['brain_state'] = json.loads(bs.read_text())
        except Exception:
            pass
        return result

    def get_stats(self):
        convs = list((MEMORY_DIR / 'conversations').glob('*.json'))
        total_msgs = 0
        for c in convs:
            try: total_msgs += len(json.loads(c.read_text()))
            except: pass
        people = {}
        pf = MEMORY_DIR / 'people.json'
        if pf.exists():
            try: people = json.loads(pf.read_text())
            except: pass
        pending_tasks = 0
        tf = BRIDGE_DIR / 'tasks-for-claude.json'
        if tf.exists():
            try: pending_tasks = len([t for t in json.loads(tf.read_text()) if t.get('status') == 'pending'])
            except: pass
        exec_log = []
        ef = MEMORY_DIR / 'exec_log.json'
        if ef.exists():
            try: exec_log = json.loads(ef.read_text())
            except: pass
        return {
            'total_conversations': len(convs),
            'total_messages': total_msgs,
            'people_tracked': len(people),
            'pending_claude_tasks': pending_tasks,
            'actions_executed': len(exec_log),
            'uptime': time.strftime('%Y-%m-%d %H:%M'),
        }

    def get_conversations(self):
        result = []
        conv_dir = MEMORY_DIR / 'conversations'
        for f in sorted(conv_dir.glob('*.json'), key=os.path.getmtime, reverse=True)[:10]:
            try:
                msgs = json.loads(f.read_text())
                phone = f.stem
                if '@newsletter' in phone: continue
                last_msg = msgs[-1] if msgs else {}
                result.append({
                    'phone': phone,
                    'last_message': last_msg.get('content', '')[:100],
                    'last_role': last_msg.get('role', ''),
                    'last_time': last_msg.get('timestamp', ''),
                    'total': len(msgs),
                })
            except: pass
        return result

    def get_people(self):
        pf = MEMORY_DIR / 'people.json'
        if pf.exists():
            try: return json.loads(pf.read_text())
            except: pass
        return {}

    def get_actions(self):
        ef = MEMORY_DIR / 'exec_log.json'
        if ef.exists():
            try: return json.loads(ef.read_text())[-20:]
            except: pass
        return []

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), DashboardHandler)
    print('Dashboard API running on :8080')
    server.serve_forever()
