import os
import json
import asyncio
import httpx
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = os.getenv("SENDER_NAME")




async def send_email(to_email: str, to_name: str, subject: str, html_content: str):
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"email": SENDER_EMAIL, "name": SENDER_NAME},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"Email uspjesno poslat na: {to_email}")
        else:
            print(f"Greska pri slanju emaila: {response.status_code} — {response.text}")


def build_order_confirmed_email(data: dict) -> tuple[str, str]:
    order_id = data.get("order_id", "N/A")
    user_name = data.get("user_name", "Potrosac")
    total_price = data.get("total_price", 0)
    items = data.get("items", [])

    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('naziv', '')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('velicina', '')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('boja', '')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('kolicina', 1)}x</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('cijena', 0)} RSD</td>
        </tr>
        """

    subject = f"Potvrda narudzbine #{order_id} — Velura"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #1a1a2e; padding: 20px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0;">VELURA</h1>
            <p style="color: #cccccc; margin: 5px 0;">Online prodavnica odjeće</p>
        </div>
        <div style="padding: 30px; background-color: #ffffff;">
            <h2 style="color: #1a1a2e;">Hvala na narudzbini, {user_name}!</h2>
            <p style="color: #555;">Vasa narudzbina je uspjesno zaprimljena i trenutno se obradjuje.</p>
            <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Broj narudzbine:</strong> #{order_id}</p>
            </div>
            <h3 style="color: #1a1a2e;">Pregled narudzbine:</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #1a1a2e; color: white;">
                        <th style="padding: 10px; text-align: left;">Proizvod</th>
                        <th style="padding: 10px; text-align: left;">Velicina</th>
                        <th style="padding: 10px; text-align: left;">Boja</th>
                        <th style="padding: 10px; text-align: left;">Kol.</th>
                        <th style="padding: 10px; text-align: left;">Cijena</th>
                    </tr>
                </thead>
                <tbody>{items_html}</tbody>
            </table>
            <div style="text-align: right; margin-top: 15px; font-size: 18px;">
                <strong>Ukupno: {total_price} RSD</strong>
            </div>
            <p style="color: #555; margin-top: 30px;">
                Pracenje statusa vase narudzbine mozete obaviti u vasem profilu na nasem sajtu.
            </p>
        </div>
        <div style="background-color: #f0f0f0; padding: 15px; text-align: center;">
            <p style="color: #888; font-size: 12px; margin: 0;">© 2024 Velura Online Store. Sva prava zadrzana.</p>
        </div>
    </div>
    """
    return subject, html_content


def build_refund_email(data: dict) -> tuple[str, str]:
    order_id = data.get("order_id", "N/A")
    user_name = data.get("user_name", "Potrosac")
    reason = data.get("reason", "Nedostupnost artikla na zalihama")

    subject = f"Narudzbina #{order_id} otkazana — Velura"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #1a1a2e; padding: 20px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0;">VELURA</h1>
            <p style="color: #cccccc; margin: 5px 0;">Online prodavnica odjeće</p>
        </div>
        <div style="padding: 30px; background-color: #ffffff;">
            <h2 style="color: #c0392b;">Narudzbina otkazana</h2>
            <p style="color: #555;">Postovani {user_name},</p>
            <p style="color: #555;">
                Zalimo sto Vam moramo saopstiti da Vasa narudzbina
                <strong>#{order_id}</strong> nije mogla biti obradjena.
            </p>
            <div style="background-color: #fdf2f2; border-left: 4px solid #c0392b;
                        padding: 15px; border-radius: 3px; margin: 20px 0;">
                <p style="margin: 0; color: #c0392b;"><strong>Razlog:</strong> {reason}</p>
            </div>
            <p style="color: #555;">
                Ako je doslo do naplate, iznos ce biti refundiran u roku od 3-5 radnih dana.
            </p>
            <p style="color: #555;">
                Molimo Vas da pokusate ponovo ili nas kontaktirajte na
                <a href="mailto:support@velura.com" style="color: #1a1a2e;">support@velura.com</a>.
            </p>
        </div>
        <div style="background-color: #f0f0f0; padding: 15px; text-align: center;">
            <p style="color: #888; font-size: 12px; margin: 0;">© 2024 Velura Online Store. Sva prava zadrzana.</p>
        </div>
    </div>
    """
    return subject, html_content



async def main():
    consumer = AIOKafkaConsumer(
        "order_completed",   # šalje orders-service
        "refund_order",      # šalje product-catalog-service
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="notifications-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    await consumer.start()
    print("Notifications Consumer pokrenut — slusa 'order_completed' i 'refund_order' topice")

    try:
        async for message in consumer:
            topic = message.topic
            data = message.value
            print(f"Primljen event iz topica '{topic}': {data}")

            to_email = data.get("user_email")
            to_name = data.get("user_name", "Potrosac")

            if not to_email:
                print(f"Preskacemo event — nema user_email: {data}")
                continue

            if topic == "order_completed":
                subject, html_content = build_order_confirmed_email(data)
            elif topic == "refund_order":
                subject, html_content = build_refund_email(data)
            else:
                print(f"Nepoznat topic: {topic} — preskacemo")
                continue

            await send_email(to_email, to_name, subject, html_content)

    finally:
        await consumer.stop()
        print("Notifications Consumer zaustavljen")


if __name__ == "__main__":
    asyncio.run(main())