#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Make sure runner runs at boot

import os
import os.path
import shlex
import subprocess
import time
import sys


BUILDSLAVE_CMD = "C:\\\\mozilla-build\\\\buildbotve\\\\scripts\\\\buildslave"
RUNSLAVE_CMD = "C:\\\\mozilla-build\\\\msys\\\\bin\\\\bash.exe --login -c 'python /c/mozilla-build/runslave.py'"

BUILDBOT_PIDFILE_PATHS = [
    'C:\\\\slave\\\\twistd.pid',
    'C:\\\\slave\\\\talos-slave\\\\twistd.pid'
]


def buildbot_process_id():
    """Returns the pid of buildbot if it's running, zero otherwise
    """
    for pidfile in BUILDBOT_PIDFILE_PATHS:
        if not os.path.exists(pidfile):
            print "skipping %s" % pidfile
            continue
        with open(pidfile, 'r') as f:
            pid = int(f.read())
        try:
            os.kill(pid, 0)  # check if process is running
            return pid
        except OSError:
            print "Old pidfile still exists, deleting and continuing"
            os.remove(pidfile)
            return 0

    return 0


def main():
    if buildbot_process_id():
        print >>sys.stderr, "Buildbot already running, exiting."
        exit(1)

    if not (os.path.isfile(BUILDSLAVE_CMD)
            and os.access(BUILDSLAVE_CMD, os.X_OK)):
        print >>sys.stderr, "{} does not exist, exiting".format(BUILDSLAVE_CMD)
        exit(1)

    print "Starting buildbot via runslave.py."
    p = subprocess.Popen(shlex.split(RUNSLAVE_CMD))
    p.wait()

    pid = buildbot_process_id()
    if pid:
        print "Buildbot started successfully."
        while True:
            try:
                os.kill(pid, 0)
            except OSError:
                print "Buildbot finished."
                break
            time.sleep(5)
    else:
        print >>sys.stderr, "Buildbot failed to start, exiting runner."
        exit(1)

    exit(0)


if __name__ == '__main__':
    main()
