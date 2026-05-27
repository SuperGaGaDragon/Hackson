"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Protocol

from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, RuntimeMessage
from orchestration.policies import policy_for_mode
from orchestration.schemas import OrchestrationRequest, OrchestrationResponse


class ModelRuntimeProtocol(Protocol):
    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse: ...


class HacksonOrchestrator:
    """Apply Hackson mode policy before delegating provider calls to model runtime."""

    def __init__(self, model_runtime: ModelRuntimeProtocol):
        self.model_runtime = model_runtime

    def generate(self, request: OrchestrationRequest) -> OrchestrationResponse:
        policy = policy_for_mode(request.mode)
        model_request = ModelGenerateRequest(
            messages=[
                RuntimeMessage(role=message.role, content=message.content)
                for message in request.context_package.messages
            ],
            max_output_tokens=policy.max_output_tokens,
            temperature=policy.temperature,
            reasoning_effort=policy.reasoning_effort,
            tool_policy=policy.tool_policy,
            metadata={
                **request.metadata,
                "mode": request.mode.value,
                "conversation_id": request.conversation_id,
                "target_agent_id": request.target_agent_id,
                "orchestration_policy": policy.name,
                "prompt_hash": request.context_package.prompt_hash,
            },
        )
        model_response = self.model_runtime.generate(model_request)
        return OrchestrationResponse(
            text=model_response.text,
            model_name=model_response.model_name,
            provider=model_response.provider,
            provider_response_id=model_response.provider_response_id,
            reasoning_summary=model_response.reasoning_summary,
            tool_events=model_response.tool_events,
            policy_name=policy.name,
            reasoning_effort=policy.reasoning_effort,
            tool_policy=policy.tool_policy,
            metadata={
                "prompt_hash": request.context_package.prompt_hash,
                "token_estimate": request.context_package.token_estimate,
                "included_message_ids": request.context_package.included_message_ids,
                "included_summary_ids": request.context_package.included_summary_ids,
                "included_memory_ids": request.context_package.included_memory_ids,
            },
        )
