#! /usr/bin/env python

import sys
import os
import argparse


DOCKER_CTX = 'dockerctx'


def main(args = sys.argv[1:]):
    """
    Build a docker image for fetching/building libzerocash.
    """
    parse_args(args)

    with LineWriter('fingerprints') as w:
        for depsrc in DEPSRCS:
            w('{}  {}', depsrc.sha256, depsrc.dlname)

    with LineWriter('Dockerfile') as w:
        w('FROM debian:latest')
        w('RUN DEBIAN_FRONTEND=noninteractive apt-get -y update')

        def instdebs(debs):
            for deb in debs:
                w('RUN DEBIAN_FRONTEND=noninteractive apt-get -y install {}',
                deb)

        instdebs(DEBS_PREFETCH)

        w('WORKDIR docker-workdir')

        for depsrc in DEPSRCS:
            w('{}', depsrc.fetch_command)

        for depsrc in DEPSRCS:
            w("RUN [ $(sha256sum {} | awk '{{ print $1 }}') = {} ]",
              depsrc.dlname,
              depsrc.sha256,
              )

        instdebs(DEBS_BUILD)

        w('ADD extract.sh ./')

        for depsrc in DEPSRCS:
            srcname = 'src-{}'.format(depsrc.name)
            w('RUN ./extract.sh {} {}', srcname, depsrc.dlname)

            # Stow build:
            stowdir = '/usr/local/stow/{}'.format(depsrc.name)
            w('RUN mkdir {}', stowdir)
            w('ENV PREFIX={}', stowdir)

            w('WORKDIR {}', srcname)

            patchname = '{}.patch'.format(depsrc.name)
            if os.path.isfile(os.path.join('dockerctx', patchname)):
                print 'Incorporating patch: {}'.format(patchname)
                w('ADD {} ./', patchname)
                w('RUN patch -p1 < {}', patchname)

            for cmd in depsrc.buildinstcmds:
                if type(cmd) is list:
                    cmd = ' '.join(cmd)
                w('RUN {}', cmd)

            w('RUN cd /usr/local/stow ; stow {}', depsrc.name)

            w('WORKDIR ..')

        w('RUN ls -F')
        w('RUN find /usr/local/lib /usr/local/include -print0 | xargs -0 ls -ld')

    print 'Docker build:'
    os.execvp('docker',
              ['docker', 'build',
               '-t', 'libzerocash-build',
               DOCKER_CTX])


DEBS_PREFETCH = [
    'apt-utils',
    'wget',
    ]

DEBS_BUILD = [
    'build-essential',
    'git-core',
    'stow',
    'unzip',
    'm4',
    ]


class DepSrc (object):
    def __init__(self, name, sha256, ext, urlbase, buildinstcmds):
        self.name = name
        self.ext = ext
        self.sha256 = sha256
        self.dlname = '{name}{ext}'.format(**locals())
        self._url = '{urlbase}{name}{ext}'.format(**locals())
        self._wgetxtra = []
        self.buildinstcmds = buildinstcmds

    @property
    def fetch_command(self):
        args = ['RUN', 'wget']
        args.extend(self._wgetxtra)
        args.append(self._url)
        return ' '.join(args)


class GithubDepSrc (DepSrc):
    def __init__(self, name, sha256, user, commit, buildinstcmds):
        self.name = name
        ext = self.ext = '.tar.gz'
        self.dlname = '{name}-{commit}{ext}'.format(**locals())
        self.sha256 = sha256
        self._url = 'https://github.com/{user}/{name}/archive/{commit}{ext}'.format(**locals())
        self._wgetxtra = ['-O', self.dlname]
        self.buildinstcmds = buildinstcmds


DEPSRCS = [
    DepSrc(
        name='gmp-6.0.0a',
        sha256='7f8e9a804b9c6d07164cf754207be838ece1219425d64e28cfa3e70d5c759aaf',
        ext='.tar.bz2',
        urlbase='https://gmplib.org/download/gmp/',
        buildinstcmds=[
            ['./configure', '--prefix=$PREFIX',
             '--enable-cxx', '--disable-shared',
            ],
            "make CPPFLAGS='-fPIC'",
            'make install',
        ],
    ),
    DepSrc(
        name='boost_1_57_0',
        sha256='910c8c022a33ccec7f088bd65d4f14b466588dda94ba2124e78b8c57db264967',
        ext='.tar.bz2',
        urlbase='http://sourceforge.net/projects/boost/files/boost/1.57.0/',
        buildinstcmds=[
            ['./bootstrap.sh', '--without-icu',
             '--with-libraries={}'.format(
                 ','.join([
                     'chrono', 'filesystem', 'program_options',
                     'system', 'thread', 'test',
                 ])),
            ],
            #['./b2', '-d2', '-j2', '-d1',
            # '--prefix=$PREFIX',
            # '--layout=tagged',
            # '--build-type=complete',
            # 'stage'],
            ['./b2', '-d0', '-j4',
             '--prefix=$PREFIX',
             '--layout=tagged',
             '--build-type=complete',
             'install'],
        ],
    ),
    DepSrc(
        name='openssl-1.0.1k',
        sha256='8f9faeaebad088e772f4ef5e38252d472be4d878c6b3a2718c10a4fcebe7a41c',
        ext='.tar.gz',
        urlbase='https://www.openssl.org/source/',
        buildinstcmds=[
            'sed -i.old "/define DATE/d" util/mkbuildinf.pl',
            'sed -i.old "s|engines apps test|engines|" Makefile.org',
            ['./Configure', '--prefix=${PREFIX}', 'no-zlib', 'no-shared',
             'no-dso', 'no-krb5', 'no-camellia', 'no-capieng', 'no-cast',
             'no-cms', 'no-dtls1', 'no-gost', 'no-gmp', 'no-heartbeats',
             'no-idea', 'no-jpake', 'no-md2', 'no-mdc2', 'no-rc5',
             'no-rdrand', 'no-rfc3779', 'no-rsax', 'no-sctp', 'no-seed',
             'no-sha0', 'no-static_engine', 'no-whirlpool', 'no-rc2',
             'no-rc4', 'no-ssl2', 'no-ssl3', 'linux-x86_64'],
            'make depend',
            'make -j1 build_libs libcrypto.pc libssl.pc openssl.pc',
            'make INSTALL_PREFIX=${PREFIX} -j1 install_sw',
        ],
    ),
    DepSrc(
        name='cryptopp562',
        sha256='5cbfd2fcb4a6b3aab35902e2e0f3b59d9171fee12b3fc2b363e1801dfec53574',
        ext='.zip',
        urlbase='http://www.cryptopp.com/',
        buildinstcmds=[
            "make static CXXFLAGS='-DNDEBUG -g -O2 -fPIC'",
            'make install PREFIX=${PREFIX}',
        ],
    ),
    GithubDepSrc(
        name='xbyak',
        sha256='467a9037c29bc417840177f3ff5d76910d3f688f2f216dd86ced4a7ac837bfb0',
        user='herumi',
        commit='62fd6d022acd83209e2a5af8ec359a3a1bed3a50',
        buildinstcmds=[
            'make install PREFIX=${PREFIX}',
        ],
    ),
    GithubDepSrc(
        name='ate-pairing',
        sha256='37c05b4a60653b912a0130d77ac816620890d65a51dd9629ed65c15b54c2d8e0',
        user='herumi',
        commit='dd7889f2881e66f87165fcd180a03cf659bcb073',
        buildinstcmds=[
            ['make', '-j', 'SUPPORT_SNARK=1',
             'INC_DIR=-I../include',
             'LIB_DIR=-L../lib'],
            'cp -rv include/ lib/ ${PREFIX}',
        ],
    ),
    GithubDepSrc(
        name='libsnark',
        sha256='b5ec84a836d0d305407d5f39c8176bae2bb448abe802a8d11ba0f88f17e6d358',
        user='scipr-lab',
        commit='69f312f149cc4bd8def8e2fed26a7941ff41251d',
        buildinstcmds=[
            # FIXME: Apply patch file from zerocashd ./depends
            ['CXXFLAGS="-fPIC"', 'make', 'lib', 'DEPINST=${PREFIX}',
             'CURVE=ALT_BN128', 'NO_PROCPS=1', 'NO_GTEST=1', 'NO_DOCS=1',
             'STATIC=1', 'NO_SUPERCOP=1'],
            ['make', 'install', 'STATIC=1', 'DEPINST=${PREFIX}',
             'PREFIX=${PREFIX}', 'CURVE=ALT_BN128', 'NO_SUPERCOP=1'],
        ],
    ),
]


def parse_args(args):
    p = argparse.ArgumentParser(description=main.__doc__)
    return p.parse_args(args)


class LineWriter (object):
    def __init__(self, name):
        self._name = name
        self._f = None

    def __enter__(self):
        path = os.path.join(DOCKER_CTX, self._name)
        print 'Generating {!r}.'.format(path)
        self._f = file(path, 'w')
        return self

    def __exit__(self, *a, **kw):
        self._f.flush()
        self._f.close()

    def __call__(self, tmpl, *args, **kw):
        self._f.write(tmpl.format(*args, **kw) + '\n')


if __name__ == '__main__':
    main()
