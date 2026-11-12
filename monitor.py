#!/usr/bin/env python3
"""Kriptomagazin Slack uptime monitor: stdlib only, no API charges."""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TARGETS = [
    'https://kriptomagazin.si/test-monitoring-napaka-503',
    'https://kriptomagazin.si/kripto-novice/',
]
STATE_PATH = Path('monitor_state.json')
FAIL_THRESHOLD = 2
TIMEOUT_SECONDS = 15


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def check(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'KriptomagazinMonitor/1.0 (uptime check)', 'Accept': 'text/html'})
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
        error = None if 200 <= status < 400 else f'HTTP {status}'
    except urllib.error.HTTPError as exc:
        status, error = exc.code, f'HTTP {exc.code}'
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        status, error = None, f'Povezava ni uspela ({type(exc).__name__})'
    elapsed = round((time.monotonic() - started)*1000)
    return status, error, elapsed


def send_slack(message):
    webhook = os.environ.get('SLACK_WEBHOOK_URL', '')
    if not webhook.startswith('https://hooks.slack.com/services/'):
        print('ERROR: nastavitev SLACK_WEBHOOK_URL manjka ali ni veljavna.', file=sys.stderr)
        return False
    request = urllib.request.Request(webhook, data=json.dumps({'text': message}).encode('utf-8'), headers={'Content-Type': 'application/json; charset=utf-8'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            body = response.read().decode('utf-8', errors='replace')
            if response.status != 200 or body.strip() != 'ok':
                raise RuntimeError(f'Slack status {response.status}')
        return True
    except (urllib.error.URLError, TimeoutError, OSError, RuntimeError) as exc:
        print(f'ERROR: Slack obvestila ni bilo mogoče poslati ({type(exc).__name__})', file=sys.stderr)
        return False


def run():
    if not os.environ.get('SLACK_WEBHOOK_URL'):
        print('ERROR: GitHub secret SLACK_WEBHOOK_URL ni nastavljen.', file=sys.stderr)
        return 2
    try:
        state = json.loads(STATE_PATH.read_text(encoding='utf-8'))
        if not isinstance(state, dict):
            raise ValueError('Wrong state type')
    except (OSError, ValueError):
        state = {}
    failed_delivery = False
    for url in TARGETS:
        code, problem, elapsed = check(url)
        previous = state.get(url, {})
        failed = int(previous.get('failed', 0)) if isinstance(previous, dict) else 0
        incident = bool(previous.get('incident', False)) if isinstance(previous, dict) else False
        if problem:
            failed += 1
            print(f'ERROR {url} {problem} ({failed} zaporednih preverjanj)')
            if failed >= FAIL_THRESHOLD and not incident:
                msg = f'🚨 *KRIPTOMAGAZIN – IZPAD*\n*Čas:* {now()}\n*URL:* {url}\n*Napaka:* {problem}\n*Zaporednih napak:* {failed}\n_Bot preverja dosegljivost. Natančen vzrok je treba preveriti v strežniških dnevnikih._'
                if send_slack(msg):
                    incident = True
                else:
                    failed_delivery = True
        else:
            print(f'OK {url} HTTP {code} ({elapsed} ms)')
            failed = 0
            if incident:
                msg = f'✅ *KRIPTOMAGAZIN – PONOVNO DELUJE*\n*Čas:* {now()}\n*URL:* {url}\n*Status:* HTTP {code}\n*Odziv:* {elapsed} ms'
                if send_slack(msg):
                    incident = False
                else:
                    failed_delivery = True
        state[url] = {'failed': failed, 'incident': incident}
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return 1 if failed_delivery else 0


if __name__ == '__main__':
    sys.exit(run())
