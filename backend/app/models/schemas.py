from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any

AuditMode = Literal["direct", "proxy", "limited"]
Domain = Literal["hiring", "lending", "healthcare", "education", "criminal_justice"]


class MetricResponse(BaseModel):
    metric_name: str
    score: Optional[float] = None
    threshold: Optional[float] = None
    is_safe: bool = False
    subgroup_breakdown: Optional[List[Dict[str, Any]]] = None


class AuditResult(BaseModel):
    audit_id: str
    mode: AuditMode
    domain: Domain
    dataset_rows: int
    status: str
    metrics: Dict[str, MetricResponse]
    findings: List[str]
    proxy_risk: Optional[float] = None
    gemini_summary: Optional[str] = None


class UploadRequest(BaseModel):
    file_url: str
    domain: Domain
    target_attribute: str
    protected_attributes: List[str]
    proxy_attributes: Optional[List[str]] = None
    confidence_threshold: float = 0.9


class AuditRequest(BaseModel):
    dataset_id: str
    mode: AuditMode
    domain: Domain
    target_attribute: str
    protected_attributes: List[str]
    proxy_attributes: Optional[List[str]] = None
    confidence_threshold: float = Field(default=0.9, ge=0.0, le=1.0)


class MitigationRequest(BaseModel):
    audit_id: str
    mitigation_type: Literal["reweighting", "threshold_optimization", "correlation_remover"]
    target_metric: str
    accuracy_cost_acceptable: float = Field(default=0.05, ge=0.0, le=1.0)