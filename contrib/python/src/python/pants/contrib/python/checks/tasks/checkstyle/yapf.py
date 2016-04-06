# coding=utf-8
# Copyright 2015 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

import logging
import shlex

from yapf import main as yapf_main

from pants.contrib.python.checks.tasks.checkstyle.common import CheckstylePlugin, Nit


# stop all logging from yapf, it's very verbose
logging.getLogger("yapf").setLevel(logging.CRITICAL)


class YapfError(Nit):
  """ matching the exit codes when running yapf on the cli """
  yapf_error = 'Y001'
  modified_files = 'Y002'
  unknown_error = 'Y999'

  exit_codes_to_nit_code = {
    1: yapf_error,
    2: modified_files,
  }

  def __init__(self, exit_code, python_file):
    super(YapfError, self).__init__(
        self.exit_codes_to_nit_code.get(exit_code, self.unknown_error),
        Nit.ERROR,
        python_file,
        'hi', # TODO
        1)

  @classmethod
  def get_error_code(cls, message):
    return cls.CLASS_ERRORS.get(message.__class__.__name__, 'F999')


class YapfChecker(CheckstylePlugin):
  """Attempts to autoformat code, raising a nit if the code was not already autoformatted."""

  def nits(self):
    """ we use yapf_main here rather than re-implementing yapf's option-parsing """
    # TODO: move config file into the config file
    # TODO: fix logging :-/
    config_file = 'pants-support/yapf/twitter.yapf'
    cmd = 'yapf --style={config_file} -i {filename}'.format(
            config_file=config_file, filename=self.python_file.filename)

    exit_code = yapf_main(shlex.split(cmd))

    if exit_code != 0:
      yield YapfError(exit_code, self.python_file)
