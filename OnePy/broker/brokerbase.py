class BrokerBase(object):
    def __init__(self):
        self.fill = None

    def execute_order(self, event):
        pass

    def set_noify(self):
        self._notify_onoff = True

    def check_after(self):
        """检查Order发送后是否执行成功"""
        return True
