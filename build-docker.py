#! /usr/bin/env python

import sys
import os
import argparse


def main(args = sys.argv[1:]):
    """
    Build a docker image for fetching/building libzerocash.
    """
    parse_args(args)

    with file(os.path.join('dockerctx', 'fingerprints'), 'w') as f:
        for depsrc in DEPSRCS:
            f.write('{}  {}\n'.format(depsrc.sha256, depsrc.dlname))

    with file(os.path.join('dockerctx', 'Dockerfile'), 'w') as df:
        wl = lambda l: df.write('{}\n'.format(l))

        for line in PRELUDE:
            wl(line)

        for deb in DEBS:
            wl(APTGET_TMPL.format(deb))

        for depsrc in DEPSRCS:
            wl(depsrc.fetch_command)

        wl('ADD fingerprints')
        wl('RUN sha256sum --check fingerprints')
        wl('RUN find')


PRELUDE = [
    'FROM debian:latest',
    'RUN apt-get -y update',
    ]

APTGET_TMPL = 'RUN DEBIAN_FRONTEND=noninteractive apt-get install {}'

DEBS = [
    'apt-utils',
    'build-essential',
    'git-core',
    'stow',
    'wget',
    ]


class DepSrc (object):
    def __init__(self, name, sha256, ext, urlbase):
        self._name = name
        self._sha256 = sha256
        self._url = '{urlbase}{name}{ext}'.format(**locals())
        self._wgetxtra = []

    @property
    def fetch_command(self):
        args = ['RUN', 'wget']
        args.extend(self._wgetxtra)
        args.append(self._url)
        return ' '.join(args)


class GithubDepSrc (DepSrc):
    def __init__(self, name, sha256, user, commit):
        ext = '.tar.gz'
        self.name = name
        self._sha256 = sha256
        self._url = 'https://github.com/{user}/{name}/archive/{commit}{ext}'.format(**locals())
        self._wgetxtra = ['-O', '{name}-{commit}{ext}'.format(**locals())]


DEPSRCS = [
    DepSrc(
        name='gmp-6.0.0a',
        sha256='7f8e9a804b9c6d07164cf754207be838ece1219425d64e28cfa3e70d5c759aaf',
        ext='.tar.bz2',
        urlbase='https://gmplib.org/download/gmp/',
    ),
    DepSrc(
        name='boost_1_57_0',
        sha256='910c8c022a33ccec7f088bd65d4f14b466588dda94ba2124e78b8c57db264967',
        ext='.tar.bz2',
        urlbase='http://sourceforge.net/projects/boost/files/boost/1.57.0/',
    ),
    DepSrc(
        name='openssl-1.0.1k',
        sha256='8f9faeaebad088e772f4ef5e38252d472be4d878c6b3a2718c10a4fcebe7a41c',
        ext='.tar.gz',
        urlbase='https://www.openssl.org/source/',
    ),
    DepSrc(
        name='cryptopp562',
        sha256='5cbfd2fcb4a6b3aab35902e2e0f3b59d9171fee12b3fc2b363e1801dfec53574',
        ext='.zip',
        urlbase='http://www.cryptopp.com/',
    ),
    GithubDepSrc(
        name='xbyak',
        sha256='467a9037c29bc417840177f3ff5d76910d3f688f2f216dd86ced4a7ac837bfb0',
        user='herumi',
        commit='62fd6d022acd83209e2a5af8ec359a3a1bed3a50',
    ),
    GithubDepSrc(
        name='ate-pairing',
        sha256='37c05b4a60653b912a0130d77ac816620890d65a51dd9629ed65c15b54c2d8e0',
        user='herumi',
        commit='dd7889f2881e66f87165fcd180a03cf659bcb073',
    ),
    GithubDepSrc(
        name='libsnark',
        sha256='b5ec84a836d0d305407d5f39c8176bae2bb448abe802a8d11ba0f88f17e6d358',
        user='scipr-lab',
        commit='69f312f149cc4bd8def8e2fed26a7941ff41251d',
    ),
]



def parse_args(args):
    p = argparse.ArgumentParser(description=main.__doc__)
    return p.parse_args(args)


if __name__ == '__main__':
    main()
