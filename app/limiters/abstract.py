from abc import ABC, abstractmethod
from typing import Optional, Tuple


class AbstractLimiter(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    async def check_and_prepare(self, session_id: Optional[str]) -> Tuple[str, bool]:
        raise NotImplementedError(
            "check_and_prepare() must be implemented by subclass."
        )

    @abstractmethod
    async def record_failure(self, session_id: str) -> None:
        raise NotImplementedError("record_failure() must be implemented by subclass.")

    @abstractmethod
    async def reset(self, session_id: Optional[str]) -> None:
        raise NotImplementedError("reset() must be implemented by subclass.")
