#!/usr/bin/env python3
"""Simple API to serve BLAI data to the dashboard."""
import json, os, glob, time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

MEMORY_DIR = Path('/home/tonny/blai-v2/memory')
CONFIG_DIR = Path('/home/tonny/blai-v2/config')
BRIDGE_DIR = Path('/home/tonny/blai-v2/claude-bridge')

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='/home/tonny/blai-v2/dashboard', **kwargs)

    def do_GET(self):
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
