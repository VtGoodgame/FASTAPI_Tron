from typing import Dict
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class AccountResource(BaseModel):
    free_net_used: int = Field(..., alias="freeNetUsed")
    free_net_limit: int = Field(..., alias="freeNetLimit")
    net_used: int = Field(..., alias="NetUsed")
    net_limit: int = Field(..., alias="NetLimit")
    total_net_limit: int = Field(..., alias="TotalNetLimit")
    total_net_weight: int = Field(..., alias="TotalNetWeight")
    total_energy_weight: int = Field(..., alias="TotalEnergyWeight")
    tron_power_limit: int = Field(..., alias="tronPowerLimit")
    tron_power_used: int = Field(..., alias="tronPowerUsed")
    energy_used: int = Field(..., alias="EnergyUsed")
    energy_limit: int = Field(..., alias="EnergyLimit")
    total_energy_limit: int = Field(..., alias="TotalEnergyLimit")
    total_energy_weight: int = Field(..., alias="TotalEnergyWeight")
    asset_net_used: Dict[str, int] = Field(default_factory=dict, alias="assetNetUsed")
    asset_net_limit: Dict[str, int] = Field(default_factory=dict, alias="assetNetLimit")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")