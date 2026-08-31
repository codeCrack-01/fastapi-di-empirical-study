from __future__ import annotations

import ast
import pathlib
from typing import Optional

from models import (
    AnnotatedDepends,
    CallableClassDep,
    DependsCall,
    FileReport,
    OverrideCall,
    RouterDepCall,
    AppDepCall,
    SecurityCall,
    YieldFunction,
)
from config import FASTAPI_DI_NAMES, FASTAPI_APP_NAMES, is_fastapi_module


class FastAPIVisitor(ast.NodeVisitor):
    def __init__(self, file_path: pathlib.Path):
        self.file_path = file_path
        self.report = FileReport(path=str(file_path))
        self._current_function: Optional[str] = None
        self._current_class: Optional[str] = None
        self._imported_names: dict[str, tuple[str, str]] = {}
        self._module_alias: dict[str, str] = {}
        self._local_defs: dict[str, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef] = {}
        self._annotated_imported = False
        self._fastapi_imported = False
        self._di_name_map: dict[str, str] = {}
        self._processed_call_locations: set[tuple[int, int]] = set()
        self._non_fastapi_depends_sources: dict[str, str] = {}

    def _resolve_import_name(self, name: str) -> Optional[str]:
        return self._di_name_map.get(name)

    def _resolve_callable(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        if isinstance(node, ast.Call):
            return self._resolve_callable(node.func)
        return None

    def _is_fastapi_di_call(self, node: ast.Call) -> bool:
        name = self._resolve_callable(node.func)
        if name is None:
            return False
        resolved = self._resolve_import_name(name)
        if resolved is None:
            return False
        return name.split(".")[-1] in FASTAPI_DI_NAMES

    def _is_fastapi_app_call(self, node: ast.Call) -> bool:
        name = self._resolve_callable(node.func)
        if name is None:
            return False
        resolved = self._resolve_import_name(name)
        return resolved is not None and name in FASTAPI_APP_NAMES

    def _is_fastapi_router_call(self, node: ast.Call) -> bool:
        name = self._resolve_callable(node.func)
        if name is None:
            return False
        resolved = self._resolve_import_name(name)
        return resolved is not None and name in {"APIRouter"}

    def _get_di_call_name(self, node: ast.Call) -> Optional[str]:
        name = self._resolve_callable(node.func)
        if name is None:
            return None
        resolved = self._resolve_import_name(name)
        if resolved is None:
            return None
        return name.split(".")[-1]

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            asname = alias.asname or alias.name
            self._module_alias[asname] = alias.name
            if is_fastapi_module(alias.name):
                self._fastapi_imported = True
                self._di_name_map[asname] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            asname = alias.asname or alias.name
            self._imported_names[asname] = (module, alias.name)
            if is_fastapi_module(module) and alias.name in FASTAPI_DI_NAMES:
                self._di_name_map[asname] = f"{module}.{alias.name}"
            if is_fastapi_module(module) and alias.name in FASTAPI_APP_NAMES:
                self._di_name_map[asname] = f"{module}.{alias.name}"
            if is_fastapi_module(module) and alias.name in {"APIRouter"}:
                self._di_name_map[asname] = f"{module}.{alias.name}"
            if alias.name in ("Depends", "Security") and not is_fastapi_module(module):
                self._non_fastapi_depends_sources[asname] = module
            if module == "typing" and alias.name == "Annotated":
                self._annotated_imported = True
            if module == "typing_extensions" and alias.name == "Annotated":
                self._annotated_imported = True
            if is_fastapi_module(module) and alias.name in {"Security"}:
                self._di_name_map[asname] = f"{module}.{alias.name}"
            if is_fastapi_module(module):
                self._fastapi_imported = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_fn = self._current_function
        self._current_function = node.name
        self._local_defs[node.name] = node
        dep_params = self._extract_signature_depends(node)
        for dep in dep_params:
            self.report.depends_calls.append(dep)
        if dep_params:
            self.report.function_defs_with_depends.append(node.name)
        self.generic_visit(node)
        has_yield_val = self._has_yield(node)
        if has_yield_val:
            self.report.yield_functions.append(
                YieldFunction(
                    line=node.lineno,
                    col=node.col_offset,
                    name=node.name,
                )
            )
        self._current_function = old_fn

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        old_fn = self._current_function
        self._current_function = node.name
        self._local_defs[node.name] = node
        dep_params = self._extract_signature_depends(node)
        for dep in dep_params:
            self.report.depends_calls.append(dep)
        if dep_params:
            self.report.function_defs_with_depends.append(node.name)
        self.generic_visit(node)
        has_yield_val = self._has_yield(node)
        if has_yield_val:
            self.report.yield_functions.append(
                YieldFunction(
                    line=node.lineno,
                    col=node.col_offset,
                    name=node.name,
                )
            )
        self._current_function = old_fn

    def _has_yield(self, node: ast.AST) -> bool:
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                return True
        return False

    def _extract_signature_depends(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[DependsCall]:
        results: list[DependsCall] = []
        all_positional = node.args.posonlyargs + node.args.args
        defaults = node.args.defaults
        offset = len(all_positional) - len(defaults)
        for i, arg in enumerate(all_positional):
            self._check_annotation_for_annotated_depends(arg)
            idx = i - offset
            if 0 <= idx < len(defaults):
                dep = self._process_default_as_depends(arg, defaults[idx])
                if dep:
                    dep.in_signature = True
                    results.append(dep)
        for i, arg in enumerate(node.args.kwonlyargs):
            self._check_annotation_for_annotated_depends(arg)
            if i < len(node.args.kw_defaults):
                dep = self._process_default_as_depends(arg, node.args.kw_defaults[i])
                if dep:
                    dep.in_signature = True
                    results.append(dep)
        return results

    @property
    def non_fastapi_depends_sources(self) -> dict[str, str]:
        return self._non_fastapi_depends_sources

    def post_process(self):
        local_class_names = {
            name for name, node in self._local_defs.items()
            if isinstance(node, ast.ClassDef)
        }
        existing_class_dep_lines = {(c.line, c.col) for c in self.report.callable_class_deps}
        for dc in self.report.depends_calls:
            key = (dc.line, dc.col)
            if dc.argument in local_class_names and key not in existing_class_dep_lines:
                self.report.callable_class_deps.append(
                    CallableClassDep(
                        line=dc.line,
                        col=dc.col,
                        class_name=dc.argument,
                        context_function=dc.context_function,
                    )
                )

    def _check_annotation_for_annotated_depends(self, arg: ast.arg):
        if arg.annotation and isinstance(arg.annotation, ast.Subscript):
            sub = arg.annotation
            anno_dep = self._check_annotated_subscript(sub)
            if anno_dep:
                self.report.annotated_depends.append(anno_dep)

    def _process_default_as_depends(self, arg: ast.arg, default_node: ast.expr) -> Optional[DependsCall]:
        if not isinstance(default_node, ast.Call):
            return None
        call = default_node
        if not self._is_fastapi_di_call(call):
            return None
        self._processed_call_locations.add((call.lineno, call.col_offset))
        call_name = self._get_di_call_name(call)
        if call_name == "Security":
            self.report.security_calls.append(
                SecurityCall(
                    line=call.lineno,
                    col=call.col_offset,
                    argument=self._serialize_args(call.args),
                    context_function=self._current_function,
                )
            )
            return None
        if call_name == "Depends":
            arg_name = self._extract_depends_arg(call)
            dep_call = DependsCall(
                line=call.lineno,
                col=call.col_offset,
                argument=arg_name,
                context_function=self._current_function,
                context_class=self._current_class,
            )
            return dep_call
        return None

    def _serialize_args(self, args: list[ast.expr]) -> str:
        parts = []
        for a in args:
            if isinstance(a, ast.Constant):
                parts.append(repr(a.value))
            elif isinstance(a, ast.Name):
                parts.append(a.id)
            elif isinstance(a, ast.List):
                parts.append("[...]")
            else:
                parts.append("...")
        return ", ".join(parts)

    def visit_Call(self, node: ast.Call):
        if not self._fastapi_imported:
            self.generic_visit(node)
            return
        call_name = self._resolve_callable(node.func)
        if call_name is None:
            self.generic_visit(node)
            return
        if (node.lineno, node.col_offset) in self._processed_call_locations:
            self.generic_visit(node)
            return
        if self._is_fastapi_di_call(node):
            resolved = self._resolve_import_name(call_name)
            short = call_name.split(".")[-1]
            if short == "Depends":
                arg_name = self._extract_depends_arg(node)
                if arg_name and arg_name in self._local_defs and isinstance(self._local_defs[arg_name], ast.ClassDef):
                    self.report.callable_class_deps.append(
                        CallableClassDep(
                            line=node.lineno,
                            col=node.col_offset,
                            class_name=arg_name,
                            context_function=self._current_function,
                        )
                    )
                if arg_name is not None and not self._is_in_signature(node):
                    self.report.depends_calls.append(
                        DependsCall(
                            line=node.lineno,
                            col=node.col_offset,
                            argument=arg_name,
                            context_function=self._current_function,
                            context_class=self._current_class,
                        )
                    )
            elif short == "Security":
                self.report.security_calls.append(
                    SecurityCall(
                        line=node.lineno,
                        col=node.col_offset,
                        argument=self._serialize_args(node.args),
                        context_function=self._current_function,
                    )
                )
        elif self._is_fastapi_router_call(node):
            deps = self._extract_dependencies_kwargs(node)
            if deps is not None:
                self.report.router_dep_calls.append(
                    RouterDepCall(
                        line=node.lineno,
                        col=node.col_offset,
                        router_name=self._extract_assignment_target(),
                        dependencies=deps,
                    )
                )
        elif self._is_fastapi_app_call(node):
            self.report.fastapi_app_count += 1
            deps = self._extract_dependencies_kwargs(node)
            if deps is not None:
                self.report.app_dep_calls.append(
                    AppDepCall(
                        line=node.lineno,
                        col=node.col_offset,
                        app_name=self._extract_assignment_target(),
                        dependencies=deps,
                    )
                )
        self.generic_visit(node)

    def _is_in_signature(self, node: ast.Call) -> bool:
        parent = getattr(node, "parent", None)
        return isinstance(parent, ast.arg) and parent.default is node

    def _extract_depends_arg(self, node: ast.Call) -> str:
        if not node.args:
            return "<empty>"
        first = node.args[0]
        return self._resolve_callable(first) or "..."

    def _extract_dependencies_kwargs(self, node: ast.Call) -> Optional[list[str]]:
        for kw in node.keywords:
            if kw.arg == "dependencies" and isinstance(kw.value, ast.List):
                result = []
                for elt in kw.value.elts:
                    if isinstance(elt, ast.Call) and self._is_fastapi_di_call(elt):
                        arg = self._extract_depends_arg(elt)
                        result.append(arg)
                    else:
                        result.append("...")
                return result
        return None

    def _extract_assignment_target(self) -> str:
        return self._current_function or "<global>"

    def _check_annotated_subscript(self, node: ast.Subscript) -> Optional[AnnotatedDepends]:
        if not self._annotated_imported:
            return None
        value_name = self._resolve_callable(node.value)
        if value_name not in ("Annotated", "typing.Annotated", "typing_extensions.Annotated"):
            return None
        slice_node = node.slice
        elements: list[ast.expr] = []
        if isinstance(slice_node, ast.Tuple):
            elements = slice_node.elts
        elif isinstance(slice_node, ast.Index) and hasattr(slice_node, "value"):
            val = slice_node.value
            if isinstance(val, ast.Tuple):
                elements = val.elts
            else:
                elements = [val]
        else:
            return None
        if len(elements) < 2:
            return None
        anno_type = self._resolve_callable(elements[0]) or "..."
        for el in elements[1:]:
            if isinstance(el, ast.Call):
                call_name = self._resolve_callable(el.func)
                if call_name and self._resolve_import_name(call_name) is not None:
                    short = call_name.split(".")[-1]
                    if short == "Depends":
                        dep_arg = self._extract_depends_arg(el)
                        return AnnotatedDepends(
                            line=node.lineno,
                            col=node.col_offset,
                            annotated_type=anno_type,
                            depends_argument=dep_arg,
                            context_function=self._current_function,
                        )
        return None

    def visit_Subscript(self, node: ast.Subscript):
        if self._annotated_imported and self._fastapi_imported:
            anno = self._check_annotated_subscript(node)
            if anno:
                self.report.annotated_depends.append(anno)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Attribute):
                attr = target.value
                if attr.attr == "dependency_overrides":
                    orig = self._resolve_callable(target.slice) or "..."
                    override = self._resolve_callable(node.value) or "..."
                    self.report.override_calls.append(
                        OverrideCall(
                            line=target.lineno,
                            col=target.col_offset,
                            original_dependency=orig,
                            override_dependency=override,
                        )
                    )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        old_class = self._current_class
        self._current_class = node.name
        self._local_defs[node.name] = node
        self.generic_visit(node)
        self._current_class = old_class

    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.value, ast.Name):
            if node.value.id in self._module_alias and node.attr in FASTAPI_DI_NAMES:
                self._di_name_map[f"{node.value.id}.{node.attr}"] = f"{self._module_alias[node.value.id]}.{node.attr}"
        self.generic_visit(node)
