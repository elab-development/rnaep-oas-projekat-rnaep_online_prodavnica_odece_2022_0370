import os
import json
import asyncio
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Narudzba

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async def main():
    """
    FZ 6.2 — Sluša refund_order topic
    Kada product-catalog nema zaliha, narudžbina se otkazuje
    """
    consumer = AIOKafkaConsumer(
        "refund_order",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="orders-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    await consumer.start()
    print("Orders Consumer pokrenut — sluša 'refund_order' topic")

    try:
        async for message in consumer:
            data = message.value
            print(f"Primljen refund_order event: {data}")

            db = SessionLocal()
            try:
                narudzba = db.query(Narudzba).filter(
                    Narudzba.id == data.get("order_id")
                ).first()

                if narudzba:
                    narudzba.status = "otkazano"
                    db.commit()
                    print(f"Narudžbina {narudzba.id} otkazana — razlog: {data.get('reason')}")
            except Exception as e:
                print(f"Greška pri otkazivanju narudžbine: {e}")
            finally:
                db.close()

    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())