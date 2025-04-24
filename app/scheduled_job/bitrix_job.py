from config import BITRIX_API_URL, BITRIX_URL
from app.models import *
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
                            file_path = os.path.join(
                                settings.MEDIA_ROOT, file_name)
                            os.makedirs(os.path.dirname(
                                file_path), exist_ok=True)
                            with open(file_path, 'wb') as f:
                                f.write(await resp.read())
                            photo_path = file_name

            car_brand = [
                item["value"] for item in product_data.get("PROPERTY_137", [])
            ] if product_data.get("PROPERTY_137") else None

            if product_data["ID"] in existing_products:
                product = existing_products[product_data["ID"]]
                product.title = product_data["NAME"]
                product.price = product_data["PRICE"]
                product.size = product_data.get("PROPERTY_107", {}).get(
                    "value") if product_data.get("PROPERTY_107") else None
                product.car_brand = car_brand
                product.type = int(product_data.get("PROPERTY_139", {}).get(
                    "value", 0)) if product_data.get("PROPERTY_139") else None
                product.photo = photo_path if photo_path else product.photo
                updated_products.append(product)
            else:
                new_products.append(Product(
                    bitrix_id=product_data["ID"],
                    title=product_data["NAME"],
                    price=product_data["PRICE"],
                    size=product_data.get("PROPERTY_107", {}).get(
                        "value") if product_data.get("PROPERTY_107") else None,
                    car_brand=car_brand,
                    type=int(product_data.get("PROPERTY_139", {}).get(
                        "value", 0)) if product_data.get("PROPERTY_139") else None,
                    photo=photo_path,
                ))

        if new_products:
            await Product.objects.abulk_create(new_products)
        if updated_products:
            await Product.objects.abulk_update(
                updated_products,
                fields=["title", "price", "size",
                        "car_brand", "type", "photo"],
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

        store_product_data_list = []
        store_product_update_list = []
        existing_store_products = {}

        store_ids = {sp["storeId"] for sp in store_products}
        product_ids = {sp["productId"] for sp in store_products}

        stores = {
            store.bitrix_id: store
            async for store in Store.objects.filter(bitrix_id__in=store_ids)
        }
        products = {
            product.bitrix_id: product
            async for product in Product.objects.filter(bitrix_id__in=product_ids)
        }

        existing_store_products = {
            ((await sp.get_store).bitrix_id, (await sp.get_product).bitrix_id): sp
            async for sp in StoreProduct.objects.filter(
                store__bitrix_id__in=store_ids, product__bitrix_id__in=product_ids
            )
        }

        for store_product_data in store_products:
            store = stores.get(str(store_product_data["storeId"]))
            product = products.get(str(store_product_data["productId"]))
            if not store or not product:
                continue

            key = (store.bitrix_id, product.bitrix_id)
            if key in existing_store_products:
                sp = existing_store_products[key]
                sp.quantity = store_product_data["amount"]
                store_product_update_list.append(sp)
            else:
                store_product_data_list.append(StoreProduct(
                    store=store,
                    product=product,
                    quantity=store_product_data["amount"],
                ))

        if store_product_data_list:
            await StoreProduct.objects.abulk_create(store_product_data_list)
        if store_product_update_list:
            await StoreProduct.objects.abulk_update(
                store_product_update_list,
                fields=["quantity"],
            )

        next_start = response.get("next")
        if not next_start:
            break
        start = next_start
        url = f"{BITRIX_API_URL}/catalog.storeproduct.list?start={start}"


async def publish_orders_to_bitrix():
    deal_url = f"{BITRIX_API_URL}/crm.deal.add"
    product_rows_url = f"{BITRIX_API_URL}/crm.deal.productrows.set"

    async for order in Order.objects.filter(published_to_bitrix=False):
        order: Order
        # Create deal in Bitrix
        request_data = {
            "fields": {
                "TITLE": order.customer_name,
                "CATEGORY_ID": 21,
                "SOURCE": "UC_9IAGE5"
            }
        }
        response = await send_request(deal_url, data=request_data, type='post')
        deal_id = response.get("result")

        if deal_id:
            # Set contact
            contact_url = f"{BITRIX_API_URL}/crm.contact.add"
            bot_user: Bot_user = await order.get_bot_user
            if not bot_user.bitrix_contact_id:
                # create new contact
                request_data = {
                    "fields": {
                        "NAME": order.customer_name,
                        "PHONE": [{
                            "ID": 12,
                            "TYPE_ID": "PHONE",
                            "VALUE": order.customer_phone,
                            "VALUE_TYPE": "MOBILE"
                        }]
                    }
                }
                response = await send_request(contact_url, data=request_data, type='post')
                contact_id = response.get("result")
                bot_user.bitrix_contact_id = contact_id
                await bot_user.asave()

            request_data = {
                "id": deal_id,
                "fields": {
                    "CONTACT_ID": bot_user.bitrix_contact_id
                }
            }
            response = await send_request(f"{BITRIX_API_URL}/crm.deal.contact.add", data=request_data, type='post')

            # Set order items as deal products
            rows = [
                {
                    "PRODUCT_ID": (await item.get_product).bitrix_id,
                    "QUANTITY": item.quantity,
                    "PRICE": int((await item.get_product).price)
                }
                async for item in order.items.all()
                if (await item.get_product).bitrix_id
            ]
            if rows:
                product_rows_data = {"id": deal_id, "rows": rows}
                product_rows_response = await send_request(
                    product_rows_url, data=product_rows_data, type='post'
                )
        order.published_to_bitrix = True
        await order.asave()
