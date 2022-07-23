from fastapi import APIRouter

from . import datastores, documents, kgs, indices, query


router = APIRouter()

router.include_router(kgs.router, prefix="/datastores/kg")
router.include_router(datastores.router, prefix="/datastores")
router.include_router(documents.router, prefix="/datastores/{datastore_name}/documents")
router.include_router(query.router, prefix="/datastores/{datastore_name}")
router.include_router(indices.router, prefix="/datastores/{datastore_name}/indices")
