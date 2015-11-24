# Synopsis

Build ``libzerocash`` in a docker container in a manner similar to
``zerocashd`` 's ``./depends`` build. So for example, this doesn't use
``libzerocash``'s ``./get-*`` scripts or ``depinst`` system.

# Usage

```bash
sudo apt-get install docker.io
python2 ./dockerctl.py
```

# Caveats

I'm new to docker, and probably making python scripts to generate docker
files is convoluted. I just don't know the best practices yet.

The [``dockerctl.py``](https://github.com/nathan-at-least/docker-libzerocash.git/blob/master/dockerctl.py)
file is messy and contains manually reproduced dependency info, based
on my reading of the zerocashd ``./depends`` package specs.  This is
almost certainly not perfect. (It's too bad the ``./depends`` system
isn't reusable in multiple projects in a compartmentalized way...)

