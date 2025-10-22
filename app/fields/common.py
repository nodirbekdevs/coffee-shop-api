from pydantic import BaseModel, Field


class ModelOrderByRule(BaseModel):
    field: str
    desc: bool = False


class CookieModel(BaseModel):
    key: str = Field(..., description="Cookie name")
    value: str = Field(..., description="Cookie value")
    max_age: int | None = Field(None, description="Lifetime in seconds")
    path: str = Field(default="/", description="Path for which the cookie is valid")
    domain: str | None = Field(default=None, description="Domain for the cookie")
    secure: bool = Field(default=False, description="Send only over HTTPS")
    httponly: bool = Field(default=True, description="Hide from JavaScript access")
    samesite: str | None = Field(
        default="lax", description="Cross-site behavior: lax, strict, none"
    )
