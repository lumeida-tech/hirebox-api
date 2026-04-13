import asyncio
import logging
import time

from litestar.testing import AsyncTestClient
from app import app

logging.basicConfig(level=logging.ERROR)

ts = int(time.time())
EMAIL = f"test{ts}@hirebox.com"
EMAIL_DOUBLON = f"doublon{ts}@hirebox.com"


async def main():
    async with AsyncTestClient(app=app) as client:

        # Register
        response = await client.post("/auth/register", json={
            "email": EMAIL,
            "password": "secret123",
            "full_name": "Test User"
        })
        print("REGISTER →", response.status_code, response.json())
        assert response.status_code == 201

        # Login
        response = await client.post("/auth/login", json={
            "email": EMAIL,
            "password": "secret123"
        })
        print("LOGIN →", response.status_code, response.json())
        assert response.status_code == 201
        assert "access_token" in response.json()

        # Mauvais mot de passe
        response = await client.post("/auth/login", json={
            "email": EMAIL,
            "password": "mauvaismdp"
        })
        print("MAUVAIS MDP →", response.status_code, response.json())
        assert response.status_code == 401

        # Doublon
        await client.post("/auth/register", json={
            "email": EMAIL_DOUBLON,
            "password": "secret123",
            "full_name": "Test User"
        })
        response = await client.post("/auth/register", json={
            "email": EMAIL_DOUBLON,
            "password": "secret123",
            "full_name": "Test User"
        })
        print("DOUBLON →", response.status_code, response.json())
        assert response.status_code == 409

        print("\n✅ Tous les tests passent")


if __name__ == "__main__":
    asyncio.run(main())