from config import BITRIX_API_URL, BITRIX_URL
from app.models import Store, Product, StoreProduct
from app.utils import send_request
import aiohttp
import os
from django.conf import settings
from django.db.models import Q


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


async def fetch_and_create_products(get_photo=False, cookie=None):
    start = 0
    url = f"{BITRIX_API_URL}/crm.product.list.json?start={start}"
    request_data = {
        "select": ["ID", "NAME", "PROPERTY_107", "PROPERTY_137", "PROPERTY_139", "PRICE", "PROPERTY_45"]
    }

    while True:
        response = await send_request(url, data=request_data, type='post')
        products = response.get("result", [])
        if not products:
            break

        bitrix_ids = [product_data["ID"] for product_data in products]
        existing_products = {
            product.bitrix_id: product
            async for product in Product.objects.filter(bitrix_id__in=bitrix_ids)
        }

        new_products = []
        updated_products = []

        for product_data in products:
            photo = product_data.get("PROPERTY_45", [])
            photo_url = BITRIX_URL + \
                photo[0]["value"]["downloadUrl"] if photo else None

            photo_path = None
            if photo_url and get_photo:
                async with aiohttp.ClientSession(headers={"Cookie": cookie}) as session:
                    async with session.get(photo_url) as resp:
                        if resp.status == 200:
                            file_name = f"products/{product_data['ID']}_{os.path.basename(photo_url)}"
                            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            with open(file_path, 'wb') as f:
                                f.write(await resp.read())
                            photo_path = file_name

            if product_data["ID"] in existing_products:
                product = existing_products[product_data["ID"]]
                product.title = product_data["NAME"]
                product.price = product_data["PRICE"]
                product.size = product_data.get("PROPERTY_107", {}).get("value") if product_data.get("PROPERTY_107") else None
                product.car_brand = product_data.get("PROPERTY_137", {}).get("value") if product_data.get("PROPERTY_137") else None
                product.type = int(product_data.get("PROPERTY_139", {}).get("value", 0)) if product_data.get("PROPERTY_139") else None
                product.photo = photo_path if photo_path else product.photo
                updated_products.append(product)
            else:
                new_products.append(Product(
                    bitrix_id=product_data["ID"],
                    title=product_data["NAME"],
                    price=product_data["PRICE"],
                    size=product_data.get("PROPERTY_107", {}).get("value") if product_data.get("PROPERTY_107") else None,
                    car_brand=product_data.get("PROPERTY_137", {}).get("value") if product_data.get("PROPERTY_137") else None,
                    type=int(product_data.get("PROPERTY_139", {}).get("value", 0)) if product_data.get("PROPERTY_139") else None,
                    photo=photo_path,
                ))

        if new_products:
            await Product.objects.abulk_create(new_products, ignore_conflicts=True)
        if updated_products:
            await Product.objects.abulk_update(
                updated_products,
                fields=["title", "price", "size", "car_brand", "type", "photo"],
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
            try:
                store = await Store.objects.aget(bitrix_id=store_product_data["storeId"])
                product = await Product.objects.aget(bitrix_id=store_product_data["productId"])
            except:
                continue
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
