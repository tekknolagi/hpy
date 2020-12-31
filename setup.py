import sys
import os
from setuptools import setup, Extension

if 'HPY_DEBUG' in os.environ:
    EXTRA_COMPILE_ARGS = ['-g', '-O0', '-UNDEBUG']
else:
    EXTRA_COMPILE_ARGS = []

def get_scm_config():
    """
    We use this function as a hook to generate version.h before building.
    """
    import textwrap
    import subprocess
    import pathlib
    import setuptools_scm

    version = setuptools_scm.get_version()
    try:
        gitrev = subprocess.check_output('git describe --abbrev=7 --dirty '
                                         '--always --tags --long'.split(), encoding='utf-8')
        gitrev = gitrev.strip()
    except subprocess.CalledProcessError:
        gitrev = "__UNKNOWN__"

    version_h = pathlib.Path('.').joinpath('hpy', 'devel', 'include', 'common', 'version.h')
    version_h.write_text(textwrap.dedent(f"""
        // automatically generated by setup.py:get_scm_config()
        #define HPY_VERSION "{version}"
        #define HPY_GIT_REVISION "{gitrev}"
    """))

    version_py = pathlib.Path('.').joinpath('hpy', 'devel', 'version.py')
    version_py.write_text(textwrap.dedent(f"""
        # automatically generated by setup.py:get_scm_config()
        __version__ = "{version}"
        __git_revision__ = "{gitrev}"
    """))

    return {} # use the default config

EXT_MODULES = []
if sys.implementation.name == 'cpython':
    EXT_MODULES += [
        Extension('hpy.universal',
                  ['hpy/universal/src/hpymodule.c',
                   'hpy/universal/src/handles.c',
                   'hpy/universal/src/ctx.c',
                   'hpy/universal/src/ctx_meth.c',
                   'hpy/universal/src/ctx_misc.c',
                   'hpy/devel/src/runtime/ctx_module.c',
                   'hpy/devel/src/runtime/ctx_type.c',
                   'hpy/devel/src/runtime/argparse.c',
                   'hpy/devel/src/runtime/ctx_tracker.c',
                   'hpy/devel/src/runtime/ctx_listbuilder.c',
                   'hpy/devel/src/runtime/ctx_tuple.c',
                   'hpy/devel/src/runtime/ctx_tuplebuilder.c',
                   'hpy/debug/src/debug_ctx.c',
                   'hpy/debug/src/debug_handles.c',
                   'hpy/debug/src/_debugmod.c',
                   'hpy/debug/src/autogen_debug_wrappers.c',
                  ],
                  include_dirs=[
                      'hpy/devel/include',
                      'hpy/universal/src',
                      'hpy/debug/src/include',
                  ],
                  extra_compile_args=[
                      '-DHPY_UNIVERSAL_ABI',
                  ] + EXTRA_COMPILE_ARGS
                  )
        ]


DEV_REQUIREMENTS = [
    "pytest",
    "pytest-xdist",
]

setup(
    name="hpy.devel",
    packages = ['hpy.devel'],
    include_package_data=True,
    extras_require={
        "dev": DEV_REQUIREMENTS,
    },
    ext_modules = EXT_MODULES,
    entry_points={
          "distutils.setup_keywords": [
              "hpy_ext_modules = hpy.devel:handle_hpy_ext_modules",
          ],
      },
    use_scm_version = get_scm_config,
    setup_requires=['setuptools_scm'],
)
