##
# Copyright 2009-2013 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
EasyBuild support for software that is configured with CMake, implemented as an easyblock

@author: Stijn De Weirdt (Ghent University)
@author: Dries Verdegem (Ghent University)
@author: Kenneth Hoste (Ghent University)
@author: Pieter De Baets (Ghent University)
@author: Jens Timmerman (Ghent University)
"""
import os

from easybuild.easyblocks.generic.configuremake import ConfigureMake
from easybuild.framework.easyconfig import CUSTOM
from easybuild.tools.filetools import run_cmd


class CMakeMake(ConfigureMake):
    """Support for configuring build with CMake instead of traditional configure script"""

    @staticmethod
    def extra_options(extra_vars=None):
        """Define extra easyconfig parameters specific to CMakeMake."""

        orig_vars = ConfigureMake.extra_options(extra_vars)
        cmakemake_vars = [
            ('srcdir', [None, "Source directory location to provide to cmake command", CUSTOM]),
            ('separate_build_dir', [False, "Perform build in a separate directory", CUSTOM]),
        ]
        cmakemake_vars.extend(orig_vars)
        return cmakemake_vars

    def configure_step(self, srcdir=None, builddir=None):
        """Configure build using cmake"""

        default_srcdir = '.'
        if self.cfg['separate_build_dir']:
            objdir = 'easybuild_obj'
            try:
                os.mkdir(objdir)
                os.chdir(objdir)
            except OSError, err:
                self.log.error("Failed to create separate build dir %s in %s: %s" % (objdir, os.getcwd(), err))
            default_srcdir = '..'

        if srcdir is None:
            if self.cfg['srcdir'] is not None:
                srcdir = self.cfg['srcdir']
            elif builddir is not None:
                self.log.deprecated("CMakeMake.configure_step: named argument 'builddir' (should be 'srcdir')", "2.0")
                srcdir = builddir
            else:
                srcdir = default_srcdir

        options = ['-DCMAKE_INSTALL_PREFIX=%s' % self.installdir]
        env_to_options = {
            'CC': 'CMAKE_C_COMPILER',
            'CFLAGS': 'CMAKE_C_FLAGS',
            'CXX': 'CMAKE_CXX_COMPILER',
            'CXXFLAGS': 'CMAKE_CXX_FLAGS',
            'F90': 'CMAKE_Fortran_COMPILER',
            'FFLAGS': 'CMAKE_Fortran_FLAGS',
        }
        for env_name, option in env_to_options.items():
            value = os.getenv(env_name)
            if value is not None:
                options.append("-D%s='%s'" % (option, value))

        options_string = " ".join(options)

        command = "%s cmake %s %s %s" % (self.cfg['preconfigopts'], srcdir, options_string, self.cfg['configopts'])
        (out, _) = run_cmd(command, log_all=True, simple=False)

        return out
