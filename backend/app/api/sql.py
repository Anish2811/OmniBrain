from fastapi import APIRouter

router = APIRouter(tags=["SQL"])


@router.post("/sql")
async def sql(query: str):

    return {
        "query": query
    }