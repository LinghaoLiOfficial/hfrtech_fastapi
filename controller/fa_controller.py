from fastapi import APIRouter, Depends

from service.fa.FAService import FAService
from utils.web.Req import Req, get_req

router = APIRouter(prefix="/fa")


@router.post("/updatePortfolioName")
async def update_portfolio_name_api(req: Req = Depends(get_req)):
    portfolio_id = await req.receive_post_param("portfolio_id")
    new_portfolio_name = await req.receive_post_param("newPortfolioName")
    token = await req.receive_header_token()

    return await FAService.update_portfolio_name(portfolio_id=portfolio_id, new_portfolio_name=new_portfolio_name, token=token)


@router.post("/deletePortfolioStock")
async def delete_portfolio_stock_api(req: Req = Depends(get_req)):
    stock_id = await req.receive_post_param("stock_id")
    portfolio_id = await req.receive_post_param("portfolio_id")
    token = await req.receive_header_token()

    return await FAService.delete_portfolio_stock(stock_id=stock_id, portfolio_id=portfolio_id, token=token)


# 重新创建全局股票信息库
@router.post("/recreateGlobalStock")
async def recreate_global_stock_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await FAService.recreate_global_stock(token=token)


@router.post("/addPortfolioStock")
async def add_portfolio_stock_api(req: Req = Depends(get_req)):
    stock_name = await req.receive_post_param("stockName")
    portfolio_id = await req.receive_post_param("portfolio_id")
    token = await req.receive_header_token()

    return await FAService.add_portfolio_stock(stock_name=stock_name, portfolio_id=portfolio_id, token=token)


@router.post("/deletePortfolio")
async def delete_portfolio_api(req: Req = Depends(get_req)):
    portfolio_id = await req.receive_post_param("portfolio_id")
    token = await req.receive_header_token()

    return await FAService.delete_portfolio(portfolio_id=portfolio_id, token=token)


@router.get("/getPortfolioList")
async def get_portfolio_list_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await FAService.get_portfolio_list(token=token)


@router.post("/addPortfolio")
async def add_portfolio_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await FAService.add_portfolio(token=token)


@router.post("/setStockSelectionConfig")
async def set_stock_selection_config_api(req: Req = Depends(get_req)):
    stock_selection_config = await req.receive_post_param("stockSelectionConfig")
    token = await req.receive_header_token()

    return await FAService.set_stock_selection_config(stock_selection_config=stock_selection_config, token=token)


@router.get("/getStockSelectionConfig")
async def get_stock_selection_config_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await FAService.get_stock_selection_config(token=token)


@router.get("/getIndustryList")
async def get_industry_list_api(req: Req = Depends(get_req)):

    return await FAService.get_industry_list()


@router.get("/getStocksDataWithImageList")
async def get_stocks_data_with_image_list_api(req: Req = Depends(get_req)):
    industry_name = await req.receive_get_param("industry_name")

    return await FAService.get_stocks_data_with_image_list(industry_name=industry_name)


@router.post("/updateStocksInfoWithImage")
async def update_stocks_info_with_image_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await FAService.update_stocks_info_with_image(token=token)


