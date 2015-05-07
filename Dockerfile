FROM ipython/scipystack

MAINTAINER Matt Edwards <matted@mit.edu>

ADD run_wrapper.py /usr/local/bin/run_wrapper.py

# This runs the wrapper script as PID 1 so that it gets all signals
# and passes them through to the child process (including the ones
# that SGE sends).

ENTRYPOINT ["/usr/bin/python", "/usr/local/bin/run_wrapper.py"]
