"""Example usage of the aiomyfox library."""
from asyncio import run

from aiomyfox.client import MyfoxClient
import httpx

CLIENT_ID = "XXX"
CLIENT_SECRET = "XXX"


async def main() -> None:
    """Run main."""
    async with httpx.AsyncClient() as httpx_client:
        myfox_client = MyfoxClient(
            httpx_client,
            CLIENT_ID,
            CLIENT_SECRET,
            redirect_uri="http://localhost:8123/auth/external/callback",
        )
        uri, state = await myfox_client.get_authorization_url()
        print("Authorization uri: ", uri)
        authorization_response = input("The authorization response url: ")
        await myfox_client.set_token_from_authorization_response(authorization_response)

        sites = await myfox_client.get_sites()
        for site in sites:
            shutters = await site.get_shutters()
            for shutter in shutters:
                await shutter.close()

            security = await site.get_security()
            print(f"Your {site.name} security status is: {security.status_label}")
            await security.set("armed")
            await myfox_client.close()


run(main())
