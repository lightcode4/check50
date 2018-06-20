"""
Functions that allow "simple" YAML checks to be converted into standard python checks
"""

import re


def _run(arg):
    return f'.run("{arg}")'


def _stdin(arg):
    if isinstance(arg, list):
        arg = r"\n".join(arg)
    return f'.stdin("{arg}", prompt=False)'


def _stdout(arg):
    if isinstance(arg, list):
        arg = r"\n".join(arg)
    return f'.stdout("{re.escape(arg)}")'


def _exit(arg):
    if arg is None:
        return ".exit()"

    try:
        arg = int(arg)
    except ValueError:
        raise InvalidArgument(f"exit command only accepts integers, not {arg}")
    return f'.exit({arg})'


COMMANDS = {"run": _run, "stdin": _stdin, "stdout": _stdout, "exit": _exit}


def compile(checks):
    """returns compiled check50 checks from config file checks in path"""

    out = ["import check50"]

    for name, check in checks.items():
        out.append(_compile_check(name, check))

    return "\n\n".join(out)


def _compile_check(name, check):
    indent = " " * 4
    out = ["@check50.check()", f"def {name}():", f'{indent}"""{name}"""']

    for run in check:
        _validate(name, run)
        _preprocess(run)

        line = [f"{indent}check50"]

        for command_name in COMMANDS:
            if command_name in run:
                line.append(COMMANDS[command_name](run[command_name]))
        out.append("".join(line))

    return "\n".join(out)


def _validate(name, run):
    for key in run:
        if key not in COMMANDS:
            raise UnsupportedCommand(
                f"{key} is not a valid command in check {name}, use only: {COMMANDS.keys()}")

    for required_command in ["run"]:
        if required_command not in run:
            raise MissingCommand(f"Missing {required_command} in check {name}")


def _preprocess(run):
    if "exit" not in run:
        run["exit"] = None


class CompileError(Exception):
    pass


class UnsupportedCommand(CompileError):
    pass


class MissingCommand(CompileError):
    pass


class InvalidArgument(CompileError):
    pass
