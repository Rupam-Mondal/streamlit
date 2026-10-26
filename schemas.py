from pydantic import BaseModel, ConfigDict, Field


class GymCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    owner_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=5, max_length=20)
    address: str = Field(min_length=5, max_length=250)


class BranchCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=5, max_length=250)
    city: str = Field(min_length=2, max_length=80)
    gym_id: int


class BranchResponse(BaseModel):
    id: int
    name: str
    address: str
    city: str
    gym_id: int

    model_config = ConfigDict(from_attributes=True)


class GymResponse(BaseModel):
    id: int
    name: str
    owner_name: str
    phone: str
    address: str
    branches: list[BranchResponse] = []

    model_config = ConfigDict(from_attributes=True)
