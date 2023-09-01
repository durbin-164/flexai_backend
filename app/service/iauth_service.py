from abc import ABC, abstractmethod


class IAuthService(ABC):
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def verify_password(self, password, hash_password) -> bool:
        raise NotImplementedError()
