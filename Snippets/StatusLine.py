#!/usr/bin/env python3

import json, asyncio, datetime, sys, logging, os
from pathlib import Path
from gi.repository import GLib
import subprocess

def sh_out(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout

# doc: https://i3wm.org/docs/i3bar-protocol.html
class Block(dict):
    DEFAULTS = {
        'full_text': '',
        'border': '#282828',
        'border_top': 0,
        'border_bottom': 2,
        'border_left': 0,
        'border_right': 0,
        'min_width': 50,
        'align': 'center',
    }

    def __init__(self, statusline, **kwargs):
        super().__init__(**self.DEFAULTS)
        super().__init__(**kwargs)
        self['name'] = self.__class__.__name__
        self['instance'] = str(id(self))
        self.statusline = statusline

    def on_click(self, event):
        self.out_once()

    def out_once(self): pass
    async def out_loop(self): pass

class BDateTime(Block):
    def out_once(self):
        self.now = datetime.datetime.now()
        self['full_text'] = self.now.strftime(' %Y/%m/%d  %H:%M')
        self.statusline.print()

    async def out_loop(self):
        while True:
            self.out_once()
            await asyncio.sleep(60 - self.now.second)

class BDisk(Block):
    def out_once(self):
        available = sh_out('df', '-h', '/').splitlines()[1].split()[3]
        self['full_text'] = f' {available}iB'
        self.statusline.print()

    async def out_loop(self):
        while True:
            self.out_once()
            await asyncio.sleep(5)

class BRAM(Block):
    def out_once(self):
        available = sh_out('free', '-h').splitlines()[1].split()[6]
        self['full_text'] = f' {available}B'
        self.statusline.print()

    async def out_loop(self):
        while True:
            self.out_once()
            await asyncio.sleep(5)

class BCPU(Block):
    def out_once(self):
        load = Path('/proc/loadavg').read_text().split()[1]
        self['full_text'] = f" {load}"
        self.statusline.print()

    async def out_loop(self):
        while True:
            self.out_once()
            await asyncio.sleep(5)

class BNetwork(Block):
    ICONS = { 'none': '', 'limited': '', 'full': '', }

    def on_click(self, event):
        if event['button'] == 1:
            subprocess.run(['nm-connection-editor'])

    def out_once(self):
        connectivity = sh_out('nmcli', '--terse', 'general').split(':')[1]
        connection = sh_out('nmcli', '--terse', 'connection', 'show',
                            '--active').split(':')
        interface = connection[3][:-1]
        name = connection[0]
        self['full_text'] = f'{self.ICONS[connectivity]} {interface} {name}'
        self.statusline.print()

    async def out_loop(self):
        self.out_once()
        monitor = await asyncio.create_subprocess_shell('nmcli monitor',
            stdout=subprocess.PIPE)
        while line := await monitor.stdout.readline():
            logging.debug(line)
            self.out_once()

# StatusLine is a status line following the i3bar input protocol.
# doc: https://i3wm.org/docs/i3bar-protocol.html
class StatusLine:
    def __init__(self):
        self.blocks = {}

    def print(self):
        print(',', json.dumps( list(self.blocks.values()) ), flush=True)

    # Read json click events sent from i3bar to stdin, and send them to the
    # corresponding blocks.
    # doc: https://i3wm.org/docs/i3bar-protocol.html#_click_events
    # ref: https://stackoverflow.com/a/36785819
    async def click_handler(self):
        while line := await self.loop.run_in_executor(None, sys.stdin.readline):
            if line.startswith('['): continue
            line = line.lstrip(',')
            event = json.loads(line)
            logging.debug(event)
            self.blocks[event['instance']].on_click(event)

    def insert(self, clsblock, **kwargs):
        block = clsblock(statusline=self, **kwargs)
        self.blocks[block['instance']] = block
        task = self.loop.create_task(block.out_loop())

    def main(self):
        # preamble
        # doc: https://i3wm.org/docs/i3bar-protocol.html#_header_in_detail
        print(json.dumps({ "version": 1, "click_events": True, }))
        print('[') # start infinite array
        print('[]') # simplify loop, subsequent items will start with ','

        # async tasks
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.click_handler())
        self.insert(BCPU)
        self.insert(BRAM)
        self.insert(BDisk)
        self.insert(BNetwork)
        self.insert(BDateTime)
        self.loop.run_forever()

if __name__ == "__main__":
    if ('-d' in sys.argv) or ('--debug' in sys.argv):
        logging.basicConfig(
            filename = Path(GLib.get_user_data_dir()) / 'dotstatus.log',
            level    = logging.DEBUG
        )

    StatusLine().main()
