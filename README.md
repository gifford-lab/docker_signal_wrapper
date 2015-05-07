# signal-wrapper

An example of a Docker container that properly handles signals and
will run in SGE (and handle `qdel`).

To apply it to other containers, copy in the wrapper script and set it
as the `ENTRYPOINT`.  Then use `docker run` normally (assuming you
didn't already have an `ENTRYPOINT`).  If you submit the job to SGE,
make sure to use `qsub -notify` so that `SIGUSR1` is sent instead of
`SIGKILL` (`SIGKILL` can't be trapped and will only stop the outer
Docker process, leaving all children still running silently).

### Example:

    qsub -N testjob -notify -j y -wd `pwd` -b y docker run --rm -i -u matted -v /etc/passwd:/etc/passwd matted/sigkilltest sleep 1h
    qdel testjob

### Details:

The Docker `ENTRYPOINT`
[documentation](https://docs.docker.com/reference/builder/#exec-form-entrypoint-example)
discusses how signals get trapped and gives other wrapper script
examples.

These [two](https://github.com/docker/docker/issues/3793)
[threads](https://github.com/docker/docker/pull/3240) on Github
discuss problems with signals and Docker, sometimes caused by
`SIGKILL` not being trapped or propagated properly.

This [mailing list
post](http://gridengine.org/pipermail/users/2014-January/007098.html)
and the `qsub` man page discuss what signals are sent to client
processes from `qdel`.

### Issues:

Right now it seems that suspending jobs doesn't work with the wrapper
script and `-notify`.  Using `-notify` changes the signals that are
passed and there are weird parent/group inconsistencies (see
[here](https://arc.liv.ac.uk/pipermail/gridengine-users/2009-May/024914.html)).
The code currently just ignores `SIGUSR1` (the suspend signal with
`-notify`), since that seems like better behavior than killing the process.

Suspending the SGE job without `-notify` (with or without the wrapper)
will only suspend the outer `docker run` process, since `SIGSTOP`
isn't passed through (at least properly, like `SIGKILL`, which we rely
on for `qdel`).  There's a chance this is a Go language bug (see
[here](https://bugzilla.redhat.com/show_bug.cgi?id=1087720)).

The right solution might be a Docker-aware queue that calls `docker
pause` (and `docker stop` to be cleaner) when appropriate, but this is
left as future work.  The current wrapper script might try to
approximate this by looking at process names or cross-referencing with
`docker top`, but that would be very hacky.
