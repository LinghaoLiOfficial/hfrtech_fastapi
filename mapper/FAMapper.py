from utils.database.SqlDriver import SqlDriver


class FAMapper:

    @classmethod
    def select_global_stock(cls, params):
        sql = "SELECT * FROM nst.fa_global_stock_detail"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_portfolio_stock_where_stock_name(cls, params):
        sql = "SELECT * FROM nst.fa_portfolio_stock_detail WHERE belong_portfolio_id = %s and stock_name = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_portfolio_stock(cls, params):
        sql = "SELECT * FROM nst.fa_portfolio_stock_detail WHERE belong_portfolio_id = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_global_stock_where_stock_name(cls, params):
        sql = "SELECT * FROM nst.fa_global_stock_detail WHERE stock_name = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_portfolio(cls, params):
        sql = "SELECT * FROM nst.fa_portfolio_detail WHERE belong_user_id = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_stock_price_where_belong_user_id_and_stock_code(cls, params):
        sql = "SELECT * FROM nst.fa_stock_price_detail WHERE belong_user_id = %s and stock_code = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_stock_price_where_industry_name(cls, params):
        sql = "SELECT * FROM nst.fa_stock_price_detail WHERE industry_name = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_stock_price(cls, params):
        sql = "SELECT * FROM nst.fa_stock_price_detail"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_stock_selection_config(cls, params):
        sql = "SELECT * FROM nst.fa_stock_selection_config WHERE belong_user_id = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def update_stock_selection_config(cls, params):
        sql = "UPDATE nst.fa_stock_selection_config SET max_stock_price_threshold = %s, recent_window_len = %s, x_axis_tick_interval = %s WHERE belong_user_id = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_stock_price(cls, params):
        sql = "INSERT INTO nst.fa_stock_price_detail (stock_id, belong_user_id, industry_code, industry_name, stock_code, stock_name, stock_price_trend_path, stock_current_price, stock_buy_refer_price, stock_sell_refer_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def update_stock_price(cls, params):
        sql = "UPDATE nst.fa_stock_price_detail SET stock_current_price = %s, stock_buy_refer_price = %s, stock_sell_refer_price = %s WHERE belong_user_id = %s and stock_code = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_portfolio(cls, params):
        sql = "INSERT INTO nst.fa_portfolio_detail (portfolio_id, portfolio_name, belong_user_id) VALUES (%s, %s, %s)"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def delete_portfolio(cls, params):
        sql = "DELETE FROM nst.fa_portfolio_detail WHERE portfolio_id = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_portfolio_stock(cls, params):
        sql = "INSERT INTO nst.fa_portfolio_stock_detail (stock_id, belong_portfolio_id, belong_user_id, stock_code, stock_name, stock_industry_name, stock_current_price) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def delete_all_global_stock(cls, params):
        sql = "DELETE FROM nst.fa_global_stock_detail"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_global_stock(cls, params):
        sql = "INSERT into nst.fa_global_stock_detail (stock_id, stock_code, stock_name, industry_name, on_star_market) VALUES (%s, %s, %s, %s, %s)"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def delete_portfolio_stock_where_portfolio_id(cls, params):
        sql = "DELETE FROM nst.fa_portfolio_stock_detail WHERE belong_portfolio_id = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def delete_portfolio_stock_where_stock_id_and_portfolio_id(cls, params):
        sql = "DELETE FROM nst.fa_portfolio_stock_detail WHERE stock_id = %s and belong_portfolio_id = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def update_portfolio_on_portfolio_name(cls, params):
        sql = "UPDATE nst.fa_portfolio_detail SET portfolio_name = %s WHERE portfolio_id = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_stock_selection_config(cls, params):
        sql = "INSERT INTO nst.fa_stock_selection_config (config_id, belong_user_id) VALUES (%s, %s)"
        return SqlDriver.execute_write(sql, params)