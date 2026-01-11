from fastapi import Depends, HTTPException, status
from app.core.deps import get_current_user

def require_roles(*required_roles):

    # ✅ flatten roles safely
    flat_required = []
    for r in required_roles:
        if isinstance(r, (list, tuple)):
            flat_required.extend(r)
        else:
            flat_required.append(r)

    flat_required = [r.upper() for r in flat_required]

    def checker(user: dict = Depends(get_current_user)):
        user_roles = [r.upper() for r in user.get("roles", [])]

        print("USER ROLES:", user_roles)
        print("REQUIRED ROLES:", flat_required)

        if not any(role in user_roles for role in flat_required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return user

    return checker


def require_super_admin():
    return require_roles("SUPER_ADMIN")

def requireORGANIZATION_ADMIN():
    return require_roles("ORGANIZATION_ADMIN")

def require_admin():
    return require_roles("ADMIN", "SUPER_ADMIN","ORGANIZATION_ADMIN")
