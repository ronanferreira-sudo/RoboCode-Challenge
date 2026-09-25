from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# ------------------------------------------------------------------
# TURMAS (CLASSROOMS)
# ------------------------------------------------------------------
class ClassroomCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class ClassroomResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    student_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ------------------------------------------------------------------
# USUÁRIOS
# ------------------------------------------------------------------
class UserRegister(BaseModel):
    username: str
    password: str
    avatar: Optional[str] = "robot-cyber"
    classroom_id: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: str
    current_password: str
    new_password: Optional[str] = None
    avatar: Optional[str] = None
    classroom_id: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: str
    xp: int
    level: int
    is_admin: bool
    classroom_id: Optional[int] = None
    classroom_name: Optional[str] = None
    classroom_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TestCaseSchema(BaseModel):
    id: int
    input_data: str
    expected_output: str
    is_hidden: bool

    class Config:
        from_attributes = True

class TestCaseCreate(BaseModel):
    input_data: Optional[str] = ""
    expected_output: str
    is_hidden: Optional[bool] = False

class ActivityCreate(BaseModel):
    phase: int
    title: str
    description: str
    difficulty: str = "EASY"
    xp_reward: int = 100
    initial_code: Optional[str] = "# Escreva seu código em Python aqui\n"
    solution_code: Optional[str] = None

class ActivityUpdate(BaseModel):
    phase: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    xp_reward: Optional[int] = None
    initial_code: Optional[str] = None
    solution_code: Optional[str] = None

class ActivityResponse(BaseModel):
    id: int
    phase: int
    title: str
    description: str
    difficulty: str
    xp_reward: int
    completed: bool = False

    class Config:
        from_attributes = True

class ActivityDetailResponse(ActivityResponse):
    initial_code: str
    test_cases: List[TestCaseSchema] = []

class ActivityAdminDetailResponse(ActivityDetailResponse):
    solution_code: Optional[str] = None

class CodeRunRequest(BaseModel):
    code: str
    input_data: Optional[str] = ""

class GenerateOutputRequest(BaseModel):
    code: str
    input_data: Optional[str] = ""

class CodeRunResult(BaseModel):
    output: str
    error: Optional[str] = None
    execution_time_ms: float

class CodeSubmissionRequest(BaseModel):
    activity_id: int
    code: str

class TestResultDetail(BaseModel):
    test_case_id: int
    passed: bool
    input_data: str
    expected_output: str
    actual_output: str
    error: Optional[str] = None

class CodeSubmissionResponse(BaseModel):
    passed: bool
    message: str
    xp_gained: int
    leveled_up: bool
    new_level: int
    new_xp: int
    results: List[TestResultDetail]

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    name: str
    avatar: str
    level: int
    xp: int
    activities_completed: int
    classroom_id: Optional[int] = None
    classroom_name: Optional[str] = None
    classroom_code: Optional[str] = None

    class Config:
        from_attributes = True
