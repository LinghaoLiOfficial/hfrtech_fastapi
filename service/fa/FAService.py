import akshare as ak
import os
from tqdm import tqdm

from mapper.FAMapper import FAMapper
from service.fa.modules.StockSelector import StockSelector
from task.TaskManager import TaskManager
from utils.common.GeneralTool import GeneralTool
from utils.common.JWTParser import JWTParser
from utils.common.StrGenerator import StrGenerator
from utils.web.Resp import Resp


class FAService:

    @classmethod
    async def update_portfolio_name(cls, portfolio_id, new_portfolio_name, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        await FAMapper.update_portfolio_on_portfolio_name({
            "portfolio_name": new_portfolio_name,
            "portfolio_id": portfolio_id
        })

        return Resp.build_success(message="更新成功")

    @classmethod
    async def delete_portfolio_stock(cls, stock_id, portfolio_id, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        await FAMapper.delete_portfolio_stock_where_stock_id_and_portfolio_id({
            "stock_id": stock_id,
            "belong_portfolio_id": portfolio_id
        })

        return Resp.build_success(message="删除成功")

    @classmethod
    async def recreate_global_stock(cls, token):
        # # 解析token
        # jwt_parser_result = JWTParser.decode_user_id(token=token)
        # if not jwt_parser_result.status:
        #     return Resp.build_jwt_error(jwt_parser_result)
        # user_id = jwt_parser_result.get_data_on_results()

        # TODO: 管理员权限检查

        task_manager = TaskManager()
        qsize = await task_manager.add_task(
            StockSelector.recreate_global_stock
        )
        print(qsize)

        return Resp.build_success()

    @classmethod
    async def add_portfolio_stock(cls, stock_name, portfolio_id, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        stock_name = stock_name.replace(" ", "").replace("*", "")

        # 判断股票名称是否正确
        mysql_result = await FAMapper.select_global_stock_where_stock_name({
            "stock_name": stock_name
        })
        if not mysql_result.verify_data_on_results():
            return Resp.build_error(
                code=50001,
                message="股票名称输入有误"
            )
        # 判断股票是否已经存在于持仓组合中
        mysql_result1 = await FAMapper.select_portfolio_stock_where_stock_name({
            "belong_portfolio_id": portfolio_id,
            "stock_name": stock_name
        })
        if mysql_result1.verify_data_on_results():
            return Resp.build_error(
                code=50002,
                message="股票已存在于持仓组合中"
            )

        # 获取股票信息
        stock_info = mysql_result.get_data_on_results()[0]

        stock_current_price_df = ak.stock_individual_info_em(symbol=stock_info["stock_code"])
        stock_current_price = stock_current_price_df.loc[stock_current_price_df['item'] == '最新', 'value'].values[0]

        await FAMapper.insert_portfolio_stock({
            "stock_id": StrGenerator.generate_uuid(),
            "belong_portfolio_id": portfolio_id,
            "belong_user_id": user_id,
            "stock_code": stock_info["stock_code"],
            "stock_name": stock_name,
            "stock_industry_name": stock_info["industry_name"],
            "stock_current_price": stock_current_price
        })

        return Resp.build_success(message="添加成功")

    @classmethod
    async def delete_portfolio(cls, portfolio_id, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        await FAMapper.delete_portfolio({
            "portfolio_id": portfolio_id
        })
        await FAMapper.delete_portfolio_stock_where_portfolio_id({
            "belong_portfolio_id": portfolio_id
        })

        return Resp.build_success(message="删除成功")

    @classmethod
    async def get_portfolio_list(cls, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        mysql_result = await FAMapper.select_portfolio({
            "belong_user_id": user_id
        })
        # 倒序排序
        my_portfolio_list = [x for x in mysql_result.get_data_on_results()][::-1]

        # 获取持仓组合的对应股票列表
        for i in range(len(my_portfolio_list)):
            mysql_result1 = await FAMapper.select_portfolio_stock({
                "belong_portfolio_id": my_portfolio_list[i]["portfolio_id"]
            })
            portfolio_stocks = mysql_result1.get_data_on_results() if mysql_result1.verify_data_on_results() else []
            # 按行业字符排序
            portfolio_stocks = sorted(portfolio_stocks, key=lambda v: v["stock_industry_name"])

            my_portfolio_list[i]["portfolio_stocks"] = portfolio_stocks

            # 获取所有的行业名称
            mysql_result2 = await FAMapper.select_global_stock({})
            all_industry_name_list = list(set([x["industry_name"] for x in mysql_result2.get_data_on_results()]))

            # 获取已经拥有的行业名称
            owned_industry_name_list = list(set([x["stock_industry_name"] for x in portfolio_stocks]))

            # 获取未拥有的行业名称
            no_display_str_list = ["-"]
            unowned_industry_name_list = [x for x in all_industry_name_list if x not in owned_industry_name_list and x not in no_display_str_list]
            # 按行业字符排序
            unowned_industry_name_list = sorted(unowned_industry_name_list)
            my_portfolio_list[i]["unowned_industry_name_list"] = unowned_industry_name_list

        return Resp.build_success(body={
            "portfolioList": my_portfolio_list
        })

    @classmethod
    async def add_portfolio(cls, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        mysql_result = await FAMapper.select_portfolio({
            "belong_user_id": user_id
        })
        my_portfolio_list = mysql_result.get_data_on_results()

        await FAMapper.insert_portfolio({
            "portfolio_id": StrGenerator.generate_uuid(),
            "portfolio_name": f"我的持仓组合 ({len(my_portfolio_list) + 1})",
            "belong_user_id": user_id
        })

        return Resp.build_success()

    @classmethod
    async def set_stock_selection_config(cls, stock_selection_config, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        await FAMapper.update_stock_selection_config({
            "max_stock_price_threshold": stock_selection_config["max_stock_price_threshold"],
            "recent_window_len": stock_selection_config["recent_window_len"],
            "x_axis_tick_interval": stock_selection_config["x_axis_tick_interval"],
            "belong_user_id": user_id
        })

        return Resp.build_success()

    @classmethod
    async def get_stock_selection_config(cls, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        mysql_result = await FAMapper.select_stock_selection_config({
            "belong_user_id": user_id
        })
        stock_selection_config = mysql_result.get_data_on_results()[0]

        # 如果参数为空，则更新为默认值
        params_to_scan_list = [
            "max_stock_price_threshold",
            "recent_window_len",
            "x_axis_tick_interval"
        ]
        stock_selection_default_config = GeneralTool.load_json(f"{GeneralTool.root_path}/service/fa/default_config/StockSelectionDefaultConfig.json")
        update_mark = False
        for param in params_to_scan_list:
            if stock_selection_config[param] is None or stock_selection_config[param] == "":
                stock_selection_config[param] = stock_selection_default_config[param]
                update_mark = True

        # 如果没有空值参数
        if not update_mark:
            return Resp.build_success(body={
                "stockSelectionConfig": stock_selection_config
            })

        # 如果有空值参数
        await FAMapper.update_stock_selection_config({
            "max_stock_price_threshold": stock_selection_config["max_stock_price_threshold"],
            "recent_window_len": stock_selection_config["recent_window_len"],
            "x_axis_tick_interval": stock_selection_config["x_axis_tick_interval"],
            "belong_user_id": user_id
        })
        mysql_result1 = await FAMapper.select_stock_selection_config({
            "belong_user_id": user_id
        })
        new_stock_selection_config = mysql_result1.get_data_on_results()[0]
        return Resp.build_success(body={
            "stockSelectionConfig": new_stock_selection_config
        })

    @classmethod
    async def get_industry_list(cls):
        industry_list = []
        industry_df = ak.stock_board_industry_name_em()
        for i in range(len(industry_df) - 1, -1, -1):
            # 排序为行业排名的降序排序（亏损大的排前面）
            # 由于当前策略关注的是低价格股，因此选择上涨股数和下跌股数，而不是涨跌幅
            try:
                industry_list.append({
                    "industry_name": industry_df.loc[i, "板块名称"],
                    "industry_code": industry_df.loc[i, "板块代码"],
                    "industry_turnover_rate": round(industry_df.loc[i, "换手率"].item(), 2),
                    "industry_rising_num": int(industry_df.loc[i, "上涨家数"].item()),
                    "industry_decline_num": int(industry_df.loc[i, "下跌家数"].item()),
                })
            except Exception as e:
                raise e

        for idx in range(len(industry_list)):
            industry_list[idx]["industry_id"] = StrGenerator.generate_uuid()

        return Resp.build_success(body={
            "industryList": industry_list
        })

    @classmethod
    async def get_stocks_data_with_image_list(cls, industry_name):
        if industry_name == "全部":
            mysql_result = await FAMapper.select_stock_price({})
        else:
            mysql_result = await FAMapper.select_stock_price_where_industry_name({
                "industry_name": industry_name
            })

        stocks_info_with_image_list = mysql_result.get_data_on_results()
        # 保留小数位
        for i in range(len(stocks_info_with_image_list)):
            stocks_info_with_image_list[i]['stock_current_price'] = round(stocks_info_with_image_list[i]['stock_current_price'], 2)
            stocks_info_with_image_list[i]['stock_buy_refer_price'] = round(stocks_info_with_image_list[i]['stock_buy_refer_price'], 2)
            stocks_info_with_image_list[i]['stock_sell_refer_price'] = round(stocks_info_with_image_list[i]['stock_sell_refer_price'], 2)
        return Resp.build_success(body={
            "stocksDataWithImageList": stocks_info_with_image_list
        })

    @classmethod
    async def update_stocks_info_with_image(cls, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        mysql_result = await FAMapper.select_stock_selection_config({
            "belong_user_id": user_id
        })
        stock_selection_config = mysql_result.get_data_on_results()[0]

        stock_price_image_path = f"storage/{user_id}/fa/stock_price"
        if not os.path.exists(stock_price_image_path):
            os.makedirs(stock_price_image_path, exist_ok=True)

        task_manager = TaskManager()
        qsize = await task_manager.add_task(
            StockSelector.update_stocks_info_with_image,
            max_stock_price=stock_selection_config["max_stock_price_threshold"],
            day_window_len=stock_selection_config["recent_window_len"],
            x_ticks_interval=stock_selection_config["x_axis_tick_interval"],
            trend_curve_type="EMA",
            period_window_list=[5],
            image_path=stock_price_image_path,
            user_id=user_id
        )
        print(qsize)

        return Resp.build_success()

