"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Protocol

from context.builder import ContextBuilder
from context.schemas import ContextBuildInput, ContextPackage
from context.service import ContextPackageService


class ContextPackageServiceProtocol(Protocol):
    def persist_package(
        self,
        *,
        user_id: str,
        package: ContextPackage,
        full_prompt_logging_enabled: bool,
    ) -> dict: ...


class ContextRuntime:
    """Single interaction-facing facade for context build and audit persistence."""

    def __init__(
        self,
        builder: ContextBuilder,
        package_service: ContextPackageServiceProtocol | None = None,
    ):
        self.builder = builder
        self.package_service = package_service

    def build(
        self,
        input_data: ContextBuildInput,
        *,
        user_id: str,
        full_prompt_logging_enabled: bool,
    ) -> ContextPackage:
        package = self.builder.build(input_data)
        if self.package_service is not None:
            self.package_service.persist_package(
                user_id=user_id,
                package=package,
                full_prompt_logging_enabled=full_prompt_logging_enabled,
            )
        return package
