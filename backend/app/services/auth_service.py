# [OWNER: M3] Auth Service Stub (T-M3-03)
class AuthService:
    """Xu ly dang ky, dang nhap va Cascade Delete tai khoan CH Play."""

    async def delete_user_cascade(self, user_id: str) -> None:
        _ = user_id
