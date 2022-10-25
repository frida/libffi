#!/usr/bin/env python3

import os
import sys
import subprocess
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional

host = os.environ.get('HOST', '')

def install_tools():
    subprocess.check_call(['pip3', 'install', 'meson==0.64.0'])
    if not shutil.which('ninja'):
        subprocess.check_call(['pip3', 'install', 'ninja'])

def print_logs(fname: str):
    log_file = Path('builddir', 'meson-logs', fname)
    if log_file.exists():
        logs = log_file.read_text(encoding='utf-8')
        print(f'::group::==== {fname} ====')
        print(logs)
        print('::endgroup::')

def build(options: List[str], skip_tests: bool, ignore_tests_errors: bool):
    # Configure, build, and run unit tests
    try:
        subprocess.check_call(['meson', 'setup', 'builddir'] + options)
        subprocess.check_call(['meson', 'compile', '-C', 'builddir'])
    except:
        print_logs('meson-log.txt')
        raise
    try:
        if not skip_tests:
            subprocess.check_call(['meson', 'test', '-C', 'builddir', '--no-rebuild'])
    except:
        print_logs('meson-log.txt')
        print_logs('testlog.txt')
        if not ignore_tests_errors:
            raise

def generate_cross_file(template: Path) -> Path:
    cpu = host.split('-')[0]
    cpu_family = cpu
    if re.match('i.86', cpu):
        cpu_family = 'x86'
    elif cpu == 'armv7a':
        cpu_family = 'arm'
    content = template.read_text()
    content = content.replace('@HOST@', host)
    content = content.replace('@CPU@', cpu)
    content = content.replace('@CPU_FAMILY@', cpu_family)
    content = content.replace('@ANDROID_NDK_ROOT@', os.environ.get('ANDROID_NDK_ROOT', ''))
    content = content.replace('@ANDROID_API_LEVEL@', os.environ.get('ANDROID_API_LEVEL', ''))
    cross_file = Path('cross.txt')
    cross_file.write_text(content)
    return cross_file

def run_in_docker(image: str, env: Optional[Dict[str, str]] = None):
    cmd = ['docker', 'run', '--rm', '-t', '-v', f'{os.getcwd()}:/opt', '--workdir', '/opt']

    env = dict(env) if env else {}
    env['QEMU_LD_PREFIX'] = f'/usr/{host}'
    for k in {'QEMU_CPU', 'LIBFFI_TEST_OPTIMIZATION'}:
        try:
            env[k] = os.environ[k]
        except KeyError:
            pass
    for k, v in env.items():
        cmd += ['-e', f'{k}={v}']

    cmd += [image, 'python3', '/opt/.ci/meson-build.py']
    print('Run in docker:', cmd)
    subprocess.check_call(cmd)

def main() -> int:
    options = ['--default-library=both']
    skip_tests = False
    cross_file = None
    ignore_tests_errors = '--ignore-tests-errors' in sys.argv

    if host == 'moxie-elf':
        options.append('--default-library=static')
        options.append('--cross-file=.ci/meson-cross-moxie.txt')
    elif 'android' in host:
        cross_file = generate_cross_file(Path('.ci/meson-cross-android.txt'))
        options.append('--cross-file=' + str(cross_file))
        skip_tests = True
    elif host == 'arm32v7-linux-gnu':
        run_in_docker('quay.io/moxielogic/arm32v7-ci-build-container:latest')
        return 0
    elif host in ['m68k-linux-gnu', 'alpha-linux-gnu', 'sh4-linux-gnu']:
        gcc_options = ' -mcpu=547x' if host == 'm68k-linux-gnu' else ''
        env = {'CC': f'{host}-gcc-8{gcc_options}',
               'CXX': f'{host}-g++-8{gcc_options}'}
        run_in_docker('quay.io/moxielogic/cross-ci-build-container:latest', env)
        return 0
    elif host in ['bfin-elf', 'm32r-elf', 'or1k-elf', 'powerpc-eabisim']:
        gcc_options = ' -msim' if host == 'bfin-elf' else ''
        env = {'CC': f'{host}-gcc{gcc_options}',
               'CXX': f'{host}-g++{gcc_options}'}
        run_in_docker(f'quay.io/moxielogic/libffi-ci-{host}', env)
        return 0

    configure_options = os.environ.get('CONFIGURE_OPTIONS', '')
    if '--disable-shared' in configure_options:
        options.append('--default-library=static')

    optimization = os.environ.get('LIBFFI_TEST_OPTIMIZATION')
    if optimization:
        options.append('-Dtests_optimizations=' + ','.join(optimization.split()))

    install_tools()
    build(options, skip_tests, ignore_tests_errors)
    if cross_file:
        cross_file.unlink()
    return 0

if __name__ == '__main__':
    exit(main())
