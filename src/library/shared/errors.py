"""Domain errors carry a stable `code`; the HTTP layer maps them, the domain
never learns about status codes."""


class DomainError(Exception):
    code = "domain_error"

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.code)


class NotFound(DomainError):
    code = "not_found"


class Conflict(DomainError):
    code = "conflict"
