

class ComputeTools:
    @classmethod
    def compute_sma(cls, data, window):
        # 计算SMA函数
        return data.rolling(window=window).mean()

    @classmethod
    def compute_ema(cls, data, window):
        # 计算EMA函数
        return data.ewm(span=window, adjust=False).mean()
