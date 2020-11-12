import logging
import argparse
import sys
from os import path
from das_shared.object_base import LoggingObject
from das_shared.op_sys import full_path, run_exec, write_to_file


APP_NAME = 'dasGenForEach'
MAX_MSvC_ARGS = 125


class GenForEachError(Exception):
    pass


class Settings(object):

    def __init__(self, argv):
        self.__args = self.__parse_argv(argv=argv)

    @classmethod
    def __parse_argv(cls, argv):
        parser = argparse.ArgumentParser(
            description='Generates DAS_FOR_EACH macros.')
        parser.add_argument('--write_to', type=str, required=True,
            help='.h file to write macros to.')
        parser.add_argument('--max_args', type=int, required=True,
            help='Maximum number of arguments.')
        parser.add_argument('--log_level', type=str,
            choices=['debug', 'info', 'warning', 'error'],
            default='info', help='Logging level. Default: %(default)s')
        return parser.parse_args(argv)

    @property
    def log_level(self):
        return getattr(logging, self.__args.log_level.upper())

    @property
    def write_to(self):
        return full_path(self.__args.write_to)

    @property
    def max_args(self):
        return int(self.__args.max_args)


class GenForEach(LoggingObject):

    def __init__(self, argv):
        self.__settings = Settings(argv=argv[1:])

    def run(self):
        logging.basicConfig(level=self.__settings.log_level,
            format='%(asctime)s [%(levelname)s:%(name)s] %(message)s')
        write_to_file(fpath=self.__settings.write_to,
            content='\n'.join(self.__generate_macros() + ['']))
        self._log_info(f'Wrote generated DAS_FOR_EACH macros to '
            f'{self.__settings.write_to}')
        self._log_info('Finished successfully.')

    def __generate_macros(self):
        max_args = self.__settings.max_args
        lines = []
        lines += [
           f'// generated by {APP_NAME}',
            '',
            '#pragma once',
            '',
            '// standard allows way simpler implementation',
            '// but this one is proven to work in MSVC',
            '',
            '#define DAS_EXPAND(x) x',
            '#define  DAS_FOR_EACH_1(WHAT, ARG, X) WHAT(X, ARG)',
        ]
        lines += self.__generate_for_each_n(
            index_min=2, index_max=min(MAX_MSvC_ARGS, max_args))
        if max_args > MAX_MSvC_ARGS:
            lines += [
                '',
                '#ifndef _MSC_VER',
                '',
            ]
            lines += self.__generate_for_each_n(
                index_min=MAX_MSvC_ARGS + 1, max_args)
            lines += [
                '',
                '#endif',
                '',
            ]
        lines += [
            '#define DAS_FOR_EACH_NARG(...) DAS_FOR_EACH_NARG_(__VA_ARGS__, DAS_FOR_EACH_RSEQ_N())',
            '#define DAS_FOR_EACH_NARG_(...) DAS_EXPAND(DAS_FOR_EACH_ARG_N(__VA_ARGS__))',
        ]

        lines += [
            '',
            '#ifndef _MSC_VER',
            '',
        ]
        lines += self.__generate_for_each_arg_n(
            max_args=max_args)
        lines += self.__generate_for_each_rseq_n(
            max_args=max_args)
        lines += [
            '',
            '#else',
            '',
        ]
        lines += self.__generate_for_each_arg_n(
            max_args=min(MAX_MSvC_ARGS, max_args))
        lines += self.__generate_for_each_rseq_n(
            max_args=min(MAX_MSvC_ARGS, max_args))
        lines += [
            '',
            '#endif',
            '',
        ]
        lines += [
            '#define CONCATENATE(x,y) x##y',
            '#define DAS_FOR_EACH_(N, what, arg, ...) DAS_EXPAND(CONCATENATE(DAS_FOR_EACH_, N)(what, arg, __VA_ARGS__))',
            '#define DAS_FOR_EACH(what, arg, ...) DAS_FOR_EACH_(DAS_FOR_EACH_NARG(__VA_ARGS__), what, arg, __VA_ARGS__)',
        ]
        return lines

    def __generate_for_each_n(self, index_min, index_max):
        return [
           f'#define DAS_FOR_EACH_{i}(WHAT, ARG, X, ...) WHAT(X, ARG) DAS_EXPAND(DAS_FOR_EACH_{i-1}(WHAT, ARG, __VA_ARGS__))'
            for i in range(index_min, index_max+1)
        ]

    def __generate_for_each_arg_n(self, indices):
        lines = []
        lines += [
            '#define DAS_FOR_EACH_ARG_N( \\',
        ]
        lines += [
            '    {} \\'.format(''.join(f'_{i+1}, '
                for i in range(max_args))),
        ]
        lines +=  [
            '    N, ...) N',
        ]
        return lines

    def __generate_for_each_rseq_n(self, max_args):
        lines = []
        lines += [
            '#define DAS_FOR_EACH_RSEQ_N() \\',
        ]
        lines += [
            '    {}'.format(', '.join(
                f'{max_args-i}' for i in range(max_args+1))),
        ]
        return lines
