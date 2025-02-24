from __future__ import annotations

import ast
import inspect
import linecache
from textwrap import dedent
from typing import Any, Callable, TypeVar

from pypeduct.transformer import PipeTransformer

T = TypeVar("T", bound=Callable[..., Any] | type[Any])


def pyped(func_or_class: T) -> T:
    """Decorator transforming >>/<< operators into pipeline operations."""
    caller_frame = inspect.currentframe().f_back
    ctx = {
        **caller_frame.f_globals,
        **caller_frame.f_locals,
    }

    try:
        source = inspect.getsource(func_or_class)
    except OSError:
        if inspect.isfunction(func_or_class):
            code = func_or_class.__code__
            lines = linecache.getlines(code.co_filename)
            source = "".join(
                lines[
                    code.co_firstlineno - 1 : code.co_firstlineno
                    + code.co_code.co_argcount
                ]
            )
            source = dedent(source.split(":", 1)[1].strip())
        else:
            raise

    tree = PipeTransformer().visit(ast.parse(dedent(source)))

    if inspect.iscoroutinefunction(func_or_class):
        ast.increment_lineno(tree, func_or_class.__code__.co_firstlineno - 1)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            node.decorator_list = [
                d
                for d in node.decorator_list
                if not (isinstance(d, ast.Name) and d.id == "pyped")
            ]

    ast.fix_missing_locations(tree)
    code = compile(
        tree, filename=ctx.get("__file__", "<pyped>"), mode="exec", optimize=2
    )
    exec(code, ctx)
    return ctx[tree.body[0].name]


if __name__ == "__main__":

    @pyped
    def test_function(x: int) -> int:
        return x >> str >> list >> len

    print(test_function(123))
