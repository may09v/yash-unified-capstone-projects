# File: /jwt_gen.py
# Location: Root directory
# Description: JWT token generation utility for testing and authentication

import jwt

# Secret used by FastAPI app (falls back to same default if env not set)
secret_key = "your-super-secret-key"


def create_jwt(user_id: str, name: str, role: str, email: str) -> str:
    """Create a JWT without expiry for local testing."""

    payload = {
        "user_id": user_id,
        "name": name,
        "role": role,
        "email": email,
        # Add exp when production hardening is required
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


if __name__ == "__main__":
    sample_users = [
        {"user_id": "EMP001", "name": "Emma Employee", "role": "employee", "email": "emma@example.com"},
        {"user_id": "IRM001", "name": "Ian IRM", "role": "irm", "email": "ian@example.com"},
        {"user_id": "SRM001", "name": "Sasha SRM", "role": "srm", "email": "sasha@example.com"},
        {"user_id": "BUH001", "name": "Bella BUH", "role": "buh", "email": "bella@example.com"},
        {"user_id": "SSU001", "name": "Sam SSUH", "role": "ssuh", "email": "sam@example.com"},
        {"user_id": "BGH001", "name": "Bianca BGH", "role": "bgh", "email": "bianca@example.com"},
        {"user_id": "SSG001", "name": "Sean SSGH", "role": "ssgh", "email": "sean@example.com"},
        {"user_id": "CFO001", "name": "Casey CFO", "role": "cfo", "email": "casey@example.com"},
        {"user_id": "MGR001", "name": "Mason Manager", "role": "manager", "email": "mason@example.com"},
        {"user_id": "TD001", "name": "Tara TravelDesk", "role": "travel_desk", "email": "tara@example.com"},
    ]

    for info in sample_users:
        token = create_jwt(info["user_id"], info["name"], info["role"], info["email"])
        print(f"Role: {info['role']}, Name: {info['name']}, ID: {info['user_id']}, Email: {info['email']}")
        print(f"JWT: {token}\n")

