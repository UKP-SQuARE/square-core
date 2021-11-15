from .dependencies import get_storage_connector


async def get_fields(conn, datastore_name: str):
    datastore = await conn.get_datastore(datastore_name)
    fields = [field.name for field in datastore.fields]
    return fields
