import httpx

API_URL = "https://effective-goggles-pvg9pqr47g9frp6-8080.app.github.dev/api/v1/accident/create"
SEND_MAIL_URL = "https://effective-goggles-pvg9pqr47g9frp6-8080.app.github.dev/api/v1/emails/send-email"

async def post_accident_data(data):
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=data)
        return response
    
async def send_mail_async_final(latitude, longitude, severity, location):
    async with httpx.AsyncClient() as client:
        response = await client.post(SEND_MAIL_URL, json={"latitude": latitude, "longitude": longitude, "severity": severity, "location": location})
        return response