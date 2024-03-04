from fastapi import FastAPI, HTTPException

from models.Deal import DealDB, Deal

app_deal = FastAPI(
    title="backend_deals"
)


@app_deal.post('/')
async def add_deal_route(deal: Deal):
    if DealDB.add_deal(deal):
        return True
    else:
        raise HTTPException(status_code=400, detail="Failed to add deal")


# Route to get a deal by ID
@app_deal.get('/get/{deal_id}')
async def get_deal(deal_id: int):
    deal = DealDB.find_deal_by_id(deal_id=deal_id)
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


# Route to delete a deal
@app_deal.post('/delete')
async def delete_deal_route(deal: Deal):
    if DealDB.delete_deal(deal):
        return True
    else:
        raise HTTPException(status_code=400, detail="Failed to delete deal")


# Route to delete a deal by ID
@app_deal.get('/delete/{deal_id}')
async def delete_deal_by_id_route(deal_id: int):
    DealDB.delete_deal_by_id(deal_id)
    return True


# Route to update a deal
@app_deal.post('/update')
async def update_deal(deal: Deal):
    if DealDB.deal_update(deal):
        return True
    else:
        raise HTTPException(status_code=404, detail="Deal not found")


# Route to list all deals for a user
@app_deal.get('/user/{telegram_id}/deals')
async def list_deals(telegram_id: int):
    deals = DealDB.find_deals_by_user(telegram_id)
    if not deals:
        return []
    return deals
