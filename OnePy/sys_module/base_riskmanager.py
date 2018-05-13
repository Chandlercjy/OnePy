from OnePy.sys_module.metabase_env import OnePyEnvBase


class RiskManagerBase(OnePyEnvBase):

    def __init__(self):
        self.env.risk_managers.update({self.__class__.__name__: self})

    def run(self):
        pass
