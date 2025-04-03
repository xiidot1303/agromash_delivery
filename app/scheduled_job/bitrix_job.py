from config import BITRIX_API_URL, BITRIX_URL
from app.models import Store, Product, StoreProduct
from app.utils import send_request


async def fetch_and_create_stores():
    url = f"{BITRIX_API_URL}/catalog.store.list"
    response = await send_request(url)
    stores = response.get("result", {}).get("stores", [])
    for store_data in stores:
        await Store.objects.aupdate_or_create(
            bitrix_id=store_data["id"],
            defaults={
                "title": store_data["title"],
                "address": store_data["address"],
            }
        )


async def fetch_and_create_products():
    start = 0
    url = f"{BITRIX_API_URL}/crm.product.list.json?start={start}"
    request_data = {
        "select": ["ID", "NAME", "PROPERTY_107", "PROPERTY_137", "PROPERTY_139", "PRICE", "PROPERTY_45"]
    }

    while True:
        response = await send_request(url, data=request_data, type='post')
        products = response.get("result", [])
        for product_data in products:
            photo = product_data.get("PROPERTY_45", [])
            photo_url = BITRIX_URL + \
                photo[0]["value"]["downloadUrl"] if photo else None

            await Product.objects.aupdate_or_create(
                bitrix_id=product_data["ID"],
                defaults={
                    "title": product_data["NAME"],
                    "price": product_data["PRICE"],
                    "size": product_data.get("PROPERTY_107", {}).get("value") if product_data.get("PROPERTY_107") else None,
                    "car_brand": product_data.get("PROPERTY_137", {}).get("value") if product_data.get("PROPERTY_137") else None,
                    "type": int(product_data.get("PROPERTY_139", {}).get("value", 0)) if product_data.get("PROPERTY_139") else None,
                    "photo": photo_url,
                }
            )

        next_start = response.get("next")
        if not next_start:
            break
        start = next_start
        url = f"{BITRIX_API_URL}/crm.product.list.json?start={start}"


async def fetch_and_create_store_products():
    start = 0
    url = f"{BITRIX_API_URL}/catalog.storeproduct.list?start={start}"

    while True:
        response = await send_request(url, type='get')
        store_products = response.get("result", {}).get("storeProducts", [])
        for store_product_data in store_products:
            store = await Store.objects.aget(bitrix_id=store_product_data["storeId"])
            product = await Product.objects.aget(bitrix_id=store_product_data["productId"])

            await StoreProduct.objects.aupdate_or_create(
                store=store,
                product=product,
                defaults={
                    "quantity": store_product_data["amount"],
                }
            )

        next_start = response.get("next")
        if not next_start:
            break
        start = next_start
        url = f"{BITRIX_API_URL}/catalog.storeproduct.list?start={start}"
