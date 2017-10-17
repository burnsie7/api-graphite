#!/usr/bin/python
"""Copyright 2013 Bryan Irvine
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

import random
import re
import sys
import time
import socket
import platform
import subprocess
import pickle
import struct

CARBON_SERVER = '127.0.0.1'
CARBON_PICKLE_PORT = 17310
DELAY = 1

def get_loadavg():
    """
    Get the load average for a unix-like system.
    For more details, "man proc" and "man uptime"
    """
    if platform.system() == "Linux":
        return open('/proc/loadavg').read().split()[:3]
    else:
        command = "uptime"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        stdout = process.communicate()[0].strip()
        # Split on whitespace and commas
        output = re.split("[\s,]+", stdout)
        return output[-3:]

def _genMetrics():
    # generate some random metrics names
    d_list = ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx']
    t_list = ['123', '456', '789', '101', '112', '131', '415']
    i_list = ['dsaf_asdf_asdf', 'qewr_qwer_qwer', 'cvxb_xcvb_xcbxv', 'hgjk_fghj_dfghj', 'asdfdgfh_sdfg_sdfg']
    d_len = len(d_list)
    t_len = len(t_list)
    i_len = len(i_list)
    met_list = []
    for i in range(d_len * t_len * i_len):
        t = t_list[random.randint(0, t_len-1)]
        d = d_list[random.randint(0, d_len-1)]
        n = i_list[random.randint(0, i_len-1)]
        met = "zuora.webapp." + d + ".prod." + n + ".storage." + t + ".save.hippo"
        met_list.append(met)
    return met_list

def run(sock, delay):
    """Make the client go go go"""
    met_list = _genMetrics()
    m_len = len(met_list)
    count = 0
    while True:
        count += 1
        now = int(time.time())
        tuples = ([])
        lines = []
        loadavg = 1
        met = met_list[random.randint(0, m_len-1)]
        tuples.append((met, (now, loadavg)))
        lines.append("%s %s %d" % (met, loadavg, now))
        message = '\n'.join(lines) + '\n' #all lines must end in a newline
        package = pickle.dumps(tuples, 1)
        size = struct.pack('!L', len(package))
        sock.sendall(size)
        sock.sendall(package)
        if count % 10000 == 0:
            print("sleep 1")
            time.sleep(1)

def main():
    """Wrap it all up together"""
    delay = DELAY
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.isdigit():
            delay = int(arg)
        else:
            sys.stderr.write("Ignoring non-integer argument. Using default: %ss\n" % delay)

    sock = socket.socket()
    try:
        sock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )
    except socket.error:
        raise SystemExit("Couldn't connect to %(server)s on port %(port)d, is carbon-cache.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PICKLE_PORT })

    try:
        run(sock, delay)
    except KeyboardInterrupt:
        sys.stderr.write("\nExiting on CTRL-c\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
