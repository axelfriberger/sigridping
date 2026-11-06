#!/usr/bin/env python3
"""Read-only Sigrid queue watcher. No third-party packages required."""
import argparse
import html.parser
import re
import subprocess
import time
import urllib.request

URL = 'https://sigrid.cs.lth.se/monitor'

class TextParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def parse_page(page, supervisor):
    parser = TextParser()
    parser.feed(page)
    text = ' '.join(parser.parts)
    if 'RoomKey(' not in text:
        if 'Aktiva rum:' in text and 'rooms:' in text:
            return {}, set()
        raise ValueError('Sidans format känns inte igen; bevakningen kan inte läsa köerna.')
    events, rooms = {}, set()
    for chunk in re.split(r'RoomKey\(', text)[1:]:
        key = re.match(r'([^,]+),\s*([^)]+)\)', chunk)
        staff = re.search(r'supervisor=Set\(([^)]*)\)', chunk)
        if not key or not staff:
            raise ValueError('Kunde inte läsa rum eller handledare.')
        if supervisor not in {s.strip() for s in staff[1].split(',')}:
            continue
        room = f'{key[1].strip()} / {key[2].strip()}'
        rooms.add(room)
        for field, label, end in [('helpQueue', 'hjälpkön', 'approvalQueue'),
                                  ('approvalQueue', 'redovisningskön', 'created')]:
            queue = re.search(field + r'=Vector\((.*?)\),\s*' + end + '=', chunk, re.S)
            if queue is None:
                raise ValueError('Kunde inte läsa ' + label)
            for name, date in re.findall(r'\(\s*([^,()]+),\s*Date\(([^)]*)\)\s*\)', queue[1]):
                # Timestamp distinguishes leaving and rejoining between polls.
                event = (room, field, name.strip(), date)
                events[event] = (room, label)
    return events, rooms

def notify(message):
    print(time.strftime('%H:%M:%S'), message, flush=True)
    # Arguments are passed as data, never inserted into AppleScript code.
    script = '''on run argv
display notification (item 1 of argv) with title "Sigrid – köbevakning" sound name "Glass"
end run'''
    try:
        result = subprocess.run(['osascript', '-e', script, message], capture_output=True, text=True)
        if result.returncode:
            print('Notisen kunde inte visas. Kontrollera notisinställningarna.', flush=True)
    except FileNotFoundError:
        print('\a', end='', flush=True)

def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--supervisor', default='axel-2')
    args.add_argument('--interval', type=float, default=10)
    args.add_argument('--test', action='store_true', help='Visa en testnotis och avsluta')
    opts = args.parse_args()
    if opts.test:
        notify('Test: här visas nya köanmälningar.')
        return
    previous, previous_rooms = set(), None
    print(f'Bevakar {opts.supervisor}. Stoppa med Ctrl+C. Datorn måste vara vaken.', flush=True)
    while True:
        try:
            request = urllib.request.Request(URL, headers={'User-Agent': 'SigridQueueNotifier/1.0'})
            with urllib.request.urlopen(request, timeout=15) as response:
                page = response.read(2_000_000).decode('utf-8')
            events, rooms = parse_page(page, opts.supervisor)
            if rooms != previous_rooms:
                print('Rum: ' + (', '.join(sorted(rooms)) or 'ingen aktiv handledarsession hittad'), flush=True)
                previous_rooms = rooms
            additions = set(events) - previous
            grouped = {}
            for event in additions:
                group = events[event]
                grouped[group] = grouped.get(group, 0) + 1
            for (room, label), count in grouped.items():
                notify(f'{room}: {count} ny(a) i {label}.')
            previous = set(events)
        except (OSError, ValueError) as error:
            print('Bevakningsfel (försöker igen):', error, flush=True)
        time.sleep(max(10, opts.interval))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nBevakningen avslutad.')
