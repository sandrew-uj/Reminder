from fastapi import FastAPI, HTTPException

from models.UnsortedDeal import UnsortedDealDB, UnsortedDeal

app_unsorted = FastAPI(
    title="backend_unsorted"
)


@app_unsorted.post('/')
async def add_deal_route(deal: UnsortedDeal):
    if UnsortedDealDB.add_deal(deal):
        return True
    else:
        raise HTTPException(status_code=400, detail="Failed to add deal")


# Route to get a deal by ID
@app_unsorted.get('/get/{deal_id}')
async def get_deal(deal_id: int):
    deal = UnsortedDealDB.find_deal_by_id(deal_id=deal_id)
    if deal is None:
        raise HTTPException(status_code=404, detail="UnsortedDeal not found")
    return deal


# Route to delete a deal
@app_unsorted.post('/delete')
async def delete_deal_route(deal: UnsortedDeal):
    if UnsortedDealDB.delete_deal(deal):
        return True
    else:
        raise HTTPException(status_code=400, detail="Failed to delete deal")


# Route to delete a deal by ID
@app_unsorted.get('/delete/{deal_id}')
async def delete_deal_by_id_route(deal_id: int):
    UnsortedDealDB.delete_deal_by_id(deal_id)
    return True


# Route to update a deal
@app_unsorted.post('/update')
async def update_deal(deal: UnsortedDeal):
    if UnsortedDealDB.deal_update(deal):
        return True
    else:
        raise HTTPException(status_code=404, detail="UnsortedDeal not found")


# Route to list all deals for a user
@app_unsorted.get('/user/{telegram_id}/deals')
async def list_deals(telegram_id: int):
    deals = UnsortedDealDB.find_deals_by_user(telegram_id)
    if not deals:
        return []
    return deals
