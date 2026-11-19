from dataclasses import dataclass

@dataclass
class Operator:
    Operator_id: str
    full_name: str
    region: str
    asset_class: str
    tenure_months: int
    kyc_verified: bool
    
@dataclass
class TelemetryRecord:
    record_id: str
    Operator_id: str
    channel: str
    record_date: str
    session_window: str
    completed_tasks: int
    distance_km: float
    active_hours: float
    gross_inflow_kes: float
    platform_fee_kes: float
    fuel_energy_cost_kes: float
    ancillary_cost_kes: float
    
    