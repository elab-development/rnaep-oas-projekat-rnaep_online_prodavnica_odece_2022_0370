import os
import json
import asyncio
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client[os.getenv("MONGODB_DB_NAME")]
products_collection = db["products"]

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

async def main():
    consumer = AIOKafkaConsumer(
        "order_completed",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="product-catalog-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )

    await consumer.start()
    await producer.start()
    print("Product Catalog Consumer pokrenut — sluša 'order_completed' topic")

    try:
        async for message in consumer:
            data = message.value
            print(f"Primljen event: {data}")

            try:
                product_id = data["product_id"]
                quantity = int(data["quantity"])
                order_id = data["order_id"]

                product = await products_collection.find_one({"_id": ObjectId(product_id)})

                if not product:
                    raise Exception(f"Proizvod {product_id} nije pronađen")

                size = data.get("size")
                color = data.get("color")
                variant_found = False

                updated_variants = []
                for variant in product.get("variants", []):
                    if variant["size"] == size and variant["color"] == color:
                        if variant["stock"] < quantity:
                            raise Exception(f"Nema dovoljno zaliha za {product['name']}")
                        variant["stock"] -= quantity
                        variant_found = True
                    updated_variants.append(variant)

                if not variant_found:
                    raise Exception(f"Varijanta velicina={size}, boja={color} nije pronađena")

                await products_collection.update_one(
                    {"_id": ObjectId(product_id)},
                    {"$set": {"variants": updated_variants}}
                )
                print(f"Zalihe smanjene za proizvod {product['name']}, kolicina: {quantity}")

            except Exception as e:
                print(f"Greška pri obradi narudžbine: {e}")
                refund_data = {
                    "order_id": data.get("order_id"),
                    "reason": str(e)
                }
                await producer.send_and_wait("refund_order", refund_data)
                print(f"Poslan refund_order event za narudžbinu {data.get('order_id')}")

    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())
