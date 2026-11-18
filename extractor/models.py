from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class DependsCall(BaseModel):
    line: int
    col: int
    argument: str
    context_function: Optional[str] = None
    context_class: Optional[str] = None
    in_signature: bool = False


class SecurityCall(BaseModel):
    line: int
    col: int
    argument: str
    scopes: list[str] = Field(default_factory=list)
    context_function: Optional[str] = None


class AnnotatedDepends(BaseModel):
    line: int
    col: int
    annotated_type: str
    depends_argument: str
    context_function: Optional[str] = None


class YieldFunction(BaseModel):
    line: int
    col: int
    name: str
    used_as_dependency: bool = False


class RouterDepCall(BaseModel):
    line: int
    col: int
    router_name: str
    dependencies: list[str] = Field(default_factory=list)


class AppDepCall(BaseModel):
    line: int
    col: int
    app_name: str
    dependencies: list[str] = Field(default_factory=list)


class OverrideCall(BaseModel):
    line: int
    col: int
    original_dependency: str
    override_dependency: str


class CallableClassDep(BaseModel):
    line: int
    col: int
    class_name: str
    context_function: Optional[str] = None


class ManualDiSite(BaseModel):
    line: int
    col: int = 0
    kind: str
    detail: str = ""
    context_function: Optional[str] = None
    evidence_type: str = ""
    confidence: str = ""


class FileReport(BaseModel):
    path: str
    is_test: bool = False
    imports_fastapi: bool = False
    depends_calls: list[DependsCall] = Field(default_factory=list)
    security_calls: list[SecurityCall] = Field(default_factory=list)
    annotated_depends: list[AnnotatedDepends] = Field(default_factory=list)
    yield_functions: list[YieldFunction] = Field(default_factory=list)
    router_dep_calls: list[RouterDepCall] = Field(default_factory=list)
    app_dep_calls: list[AppDepCall] = Field(default_factory=list)
    override_calls: list[OverrideCall] = Field(default_factory=list)
    callable_class_deps: list[CallableClassDep] = Field(default_factory=list)
    manual_di_sites: list[ManualDiSite] = Field(default_factory=list)
    ambient_state_providers: list[str] = Field(default_factory=list)
    imported_modules: set[str] = Field(default_factory=set)
    symbols_used: set[str] = Field(default_factory=set)
    container_wiring_sites: list = Field(default_factory=list)
    function_defs_with_depends: list[str] = Field(default_factory=list)
    non_fastapi_depends_sources: dict[str, str] = Field(default_factory=dict)
    fastapi_app_count: int = 0


class GraphNode(BaseModel):
    id: str
    file: str
    kind: str = "function"


class GraphEdge(BaseModel):
    source: str
    target: str
    source_file: str
    target_file: str


class DependencyGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    max_depth: int = 0
    scope: str = "production"
    unresolved_depends: int = 0


class RepoCoverage(BaseModel):
    files_total: int = 0
    files_production: int = 0
    files_test: int = 0
    pct_production: float = 0.0


class RepoMetadata(BaseModel):
    name: str
    commit_sha: str = ""
    analysis_date: str = ""


class RepoAggregate(BaseModel):
    files_importing_fastapi: int = 0
    fastapi_app_count: int = 0
    depends_total: int = 0
    security_total: int = 0
    annotated_depends_total: int = 0
    yield_dep_total: int = 0
    router_dep_total: int = 0
    app_dep_total: int = 0
    override_total: int = 0
    callable_class_dep_total: int = 0


class RepoReport(BaseModel):
    schema_version: str
    extractor_version: str
    repo: RepoMetadata
    coverage: RepoCoverage
    aggregate: RepoAggregate
    test_aggregate: Optional[RepoAggregate] = None
    file_details: list[FileReport] = Field(default_factory=list)
    dependency_graph: DependencyGraph = Field(default_factory=DependencyGraph)
    observations: list[str] = Field(default_factory=list)
