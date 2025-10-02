class DecisionTools:
    @classmethod
    def mean_decision_buy_price(cls, ma, std_num=3):
        mean_value = ma.mean()
        std_value = ma.std(ddof=0)  # 总体标准差
        buy_price = mean_value - std_num * std_value
        return buy_price.item()

    @classmethod
    def mean_decision_sell_price(cls, ma, std_num=3):
        mean_value = ma.mean()
        std_value = ma.std(ddof=0)  # 总体标准差
        sell_price = mean_value + std_num * std_value
        return sell_price.item()
