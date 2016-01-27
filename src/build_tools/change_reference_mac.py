# -*- coding: utf-8 -*-
# Copyright 2010-2016, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Change the reference to frameworks.

Typical usage:

  % change_reference_mac.py --qtdir=/path/to/qtdir/ \
      --target=/path/to/target.app/Contents/MacOS/target --branding=Mozc
"""

__author__ = "horo"

import optparse
import os

from util import PrintErrorAndExit
from util import RunOrDie


def ParseOption():
  """Parse command line options."""
  parser = optparse.OptionParser()
  parser.add_option('--qtdir', dest='qtdir')
  parser.add_option('--target', dest='target')
  parser.add_option('--branding', dest='branding')

  (opts, _) = parser.parse_args()

  return opts


def GetFrameworkPath(name, version):
  return '%s.framework/Versions/%s/%s' % (name, version, name)


def GetReferenceTo(branding, framework):
  return ('@executable_path/../../../%sTool.app/Contents/Frameworks/%s' %
          (branding, framework))


def InstallNameTool(target, reference_from, reference_to):
  cmd = ['install_name_tool', '-change', reference_from, reference_to, target]
  RunOrDie(cmd)


def main():
  opt = ParseOption()

  if not opt.qtdir:
    PrintErrorAndExit('--qtdir option is mandatory.')

  if not opt.target:
    PrintErrorAndExit('--target option is mandatory.')

  if not opt.branding:
    PrintErrorAndExit('--branding option is mandatory.')

  qtdir = os.path.abspath(opt.qtdir)
  target = os.path.abspath(opt.target)

  # Changes the reference to QtCore framework from the target application
  # From: /path/to/qt/lib/QtCore.framework/Versions/4/QtCore
  #   To: @executable_path/../../../MozcTool.app/Contents/Frameworks/...
  qtcore_framework = GetFrameworkPath('QtCore', '4')
  InstallNameTool(target,
                  '%s/lib/%s' % (qtdir, qtcore_framework),
                  GetReferenceTo(opt.branding, qtcore_framework))

  # Changes the reference to QtGui framework from the target application
  qtgui_framework = GetFrameworkPath('QtGui', '4')
  InstallNameTool(target,
                  '%s/lib/%s' % (qtdir, qtgui_framework),
                  GetReferenceTo(opt.branding, qtgui_framework))

  # Change the reference to $(branding)Tool_lib from the target application
  # From: @executable_path/../Frameworks/MozcTool_lib.framework/...
  #   To: @executable_path/../../../MozcTool.app/Contents/Frameworks/...
  toollib_framework = GetFrameworkPath('%sTool_lib' % opt.branding, 'A')
  InstallNameTool(target,
                  '@executable_path/../Frameworks/%s' % toollib_framework,
                  GetReferenceTo(opt.branding, toollib_framework))

  # Change the reference to GoogleBreakpad from the target application
  breakpad_framework = GetFrameworkPath('GoogleBreakpad', 'A')
  InstallNameTool(target,
                  '@executable_path/../Frameworks/%s' % breakpad_framework,
                  GetReferenceTo(opt.branding, breakpad_framework))


if __name__ == '__main__':
  main()