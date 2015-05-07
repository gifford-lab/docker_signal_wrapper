#!/usr/bin/env python
# 
# A script that calls another command by spawning a child process and
# then listens to signals.  It terminates or kills the child process
# if it receives certain signals, given below.
#
# Example:
# ./run_wrapper.py echo hello
# 
# Its main use is as a Docker ENTRYPOINT so that signals are handled
# appropriately when the docker run process is signalled (see the
# Dockerfile in this directory).

import signal
import sys
import time
import subprocess

process = None

def signal_handler(code, frame):
    if code == signal.SIGUSR1:
        print >>sys.stderr, "[wrapper] caught (and ignoring) signal %d" % code
        return
    print >>sys.stderr, "[wrapper] caught signal %d; killing subprocess and exiting " % code
    if process is not None:
        try:
            process.terminate()
            if process.poll() is None:
                print >>sys.stderr, "[wrapper] SIGTERM ignored; waiting and then sending SIGKILL"
                time.sleep(5)
                if process.poll() is None:
                    process.kill()
        except OSError:
            print >>sys.stderr, "[wrapper] problems killing the process, or it stopped before we killed it"
        sys.exit(process.poll())
    sys.exit(code) # shouldn't get here, unless we hit a race condition

for code in [signal.SIGUSR1, # for SGE suspend, if we use qsub -notify... need to trap it because it will kill python otherwise
             signal.SIGUSR2, # SGE qdel, if we use qsub -notify
             # signal.SIGCHLD, # signal from child when it stops normally (or otherwise)
             # signal.SIGCLD, # ditto
        ]:
    signal.signal(code, signal_handler)

if len(sys.argv) > 1:
    # non-shell version is safer, but more annoying since everything has to be a binary
    # process = subprocess.Popen(sys.argv[1:])
    process = subprocess.Popen(" ".join(sys.argv[1:]), shell=True)
    sys.exit(process.wait())
