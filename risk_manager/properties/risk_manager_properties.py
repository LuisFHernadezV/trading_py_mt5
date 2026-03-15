from pydantic import BaseModel


class BaseRiskProps(BaseModel):
    pass


class MaxLeverageRiskFactorProps(BaseRiskProps):
    max_leverage_factor: float
