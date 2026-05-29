"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip()


class UserLoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class UserQuickTryRequest(BaseModel):
    source: str = Field(default="hackathon", min_length=1, max_length=32)


class UserAgentProfile(BaseModel):
    slot: str
    name: str
    short: str
    color: str
    voice: str
    personality: str
    story: str = ""


class UserAgentProfileUpdate(BaseModel):
    slot: str = Field(pattern=r"^agent_[12]$")
    name: str = Field(min_length=1, max_length=32)
    voice: str = Field(min_length=1, max_length=80)
    personality: str = Field(min_length=1, max_length=1200)
    story: str = Field(default="", max_length=4000)


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    display_name: str | None = Field(default=None, min_length=1, max_length=64)
    idle_on: bool | None = None
    background_idle_on: bool | None = Field(default=None, alias="backgroundIdleOn")
    full_prompt_logging_on: bool | None = Field(default=None, alias="fullPromptLoggingOn")
    language_preference: str | None = Field(default=None, min_length=2, max_length=16)
    personality: str | None = Field(default=None, max_length=1200)
    story: str | None = Field(default=None, max_length=4000)
    agent_profiles: list[UserAgentProfileUpdate] | None = Field(default=None, alias="agentProfiles")


class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    username: str
    display_name: str = Field(alias="displayName")
    email: EmailStr
    idle_on: bool = Field(alias="idleOn")
    background_idle_on: bool = Field(alias="backgroundIdleOn")
    full_prompt_logging_on: bool = Field(alias="fullPromptLoggingOn")
    language_preference: str = Field(alias="languagePreference")
    personality: str = ""
    story: str = ""
    agent_profiles: list[UserAgentProfile] = Field(default_factory=list, alias="agentProfiles")
    is_temporary: bool = Field(default=False, alias="isTemporary")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class AuthResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    user: UserResponse


class DesktopHandoffBindRequest(BaseModel):
    code: str = Field(min_length=16, max_length=96, pattern=r"^[a-zA-Z0-9_-]+$")


class DesktopHandoffClaimRequest(BaseModel):
    code: str = Field(min_length=16, max_length=96, pattern=r"^[a-zA-Z0-9_-]+$")


class DesktopHandoffStatusResponse(BaseModel):
    status: str
    access_token: str | None = Field(default=None, alias="accessToken")
    token_type: str | None = Field(default=None, alias="tokenType")
    user: UserResponse | None = None


class PromptLogResponse(BaseModel):
    id: str
    conversation_id: str = Field(alias="conversationId")
    mode: str
    target_agent_id: str = Field(alias="targetAgentId")
    prompt_hash: str = Field(alias="promptHash")
    token_estimate: int = Field(alias="tokenEstimate")
    full_prompt_text: str | None = Field(default=None, alias="fullPromptText")
    full_prompt_text_expires_at: datetime | None = Field(default=None, alias="fullPromptTextExpiresAt")
    created_at: datetime = Field(alias="createdAt")


class PromptLogListResponse(BaseModel):
    prompt_logs: list[PromptLogResponse] = Field(default_factory=list, alias="promptLogs")


class PromptLogDeleteResponse(BaseModel):
    deleted_prompt_logs: int = Field(alias="deletedPromptLogs")
