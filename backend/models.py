"""
Data models for Pump.fun Risk Analyzer
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert type enumeration"""
    HOLDER_CONCENTRATION = "holder_concentration"
    LIQUIDITY_REMOVAL = "liquidity_removal"
    WASH_TRADING = "wash_trading"
    HONEYPOT = "honeypot"
    BUNDLER_ACTIVITY = "bundler_activity"
    PRICE_MANIPULATION = "price_manipulation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class TokenRisk(BaseModel):
    """Token risk assessment model"""
    token_address: str
    risk_level: RiskLevel
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    factors: Dict[str, Any]
    last_updated: datetime
    created_at: datetime


class HolderInfo(BaseModel):
    """Token holder information"""
    address: str
    balance: float
    percentage: float
    is_contract: bool = False
    first_seen: Optional[datetime] = None
    last_activity: Optional[datetime] = None


class LiquidityInfo(BaseModel):
    """Liquidity information"""
    total_liquidity: float
    locked_liquidity: float
    locked_percentage: float
    lock_duration: Optional[int] = None  # seconds
    lock_expiry: Optional[datetime] = None
    lp_token_holders: List[str]


class VolumeInfo(BaseModel):
    """Volume analysis information"""
    total_volume_24h: float
    unique_traders: int
    wash_trading_score: float
    volume_authenticity: float
    top_traders_percentage: float


class SocialInfo(BaseModel):
    """Social media information"""
    twitter_mentions: int = 0
    telegram_members: int = 0
    discord_members: int = 0
    website_exists: bool = False
    domain_age_days: Optional[int] = None
    social_sentiment: Optional[float] = None


class TokenAnalysis(BaseModel):
    """Complete token analysis model"""
    token_address: str
    token_name: Optional[str] = None
    token_symbol: Optional[str] = None
    risk_level: RiskLevel
    risk_score: float
    confidence: float
    
    # Detailed analysis
    holders: List[HolderInfo]
    liquidity: LiquidityInfo
    volume: VolumeInfo
    social: SocialInfo
    
    # Risk factors
    risk_factors: Dict[str, Any]
    
    # Metadata
    analysis_timestamp: datetime
    created_at: datetime


class Alert(BaseModel):
    """Alert model"""
    id: Optional[str] = None
    token_address: str
    alert_type: AlertType
    risk_level: RiskLevel
    title: str
    description: str
    severity: int = Field(ge=1, le=5)
    is_resolved: bool = False
    created_at: datetime
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AlertSubscription(BaseModel):
    """Alert subscription model"""
    id: Optional[str] = None
    email: str
    risk_threshold: RiskLevel
    token_addresses: Optional[List[str]] = None
    alert_types: Optional[List[AlertType]] = None
    is_active: bool = True
    created_at: datetime
    last_alert: Optional[datetime] = None


class TransactionInfo(BaseModel):
    """Transaction information"""
    signature: str
    timestamp: datetime
    type: str  # buy, sell, add_liquidity, remove_liquidity
    amount: float
    price: Optional[float] = None
    from_address: str
    to_address: str
    gas_fee: float
    success: bool


class PlatformStats(BaseModel):
    """Platform statistics"""
    total_tokens_analyzed: int
    high_risk_tokens: int
    medium_risk_tokens: int
    low_risk_tokens: int
    total_alerts: int
    active_subscriptions: int
    last_24h_analyses: int
    average_risk_score: float


class RiskFactor(BaseModel):
    """Individual risk factor"""
    name: str
    description: str
    score: float
    weight: float
    evidence: List[str]
    recommendation: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Token analysis request"""
    token_address: str
    include_social: bool = True
    include_volume: bool = True
    include_holders: bool = True
    include_liquidity: bool = True
    priority: str = "normal"  # low, normal, high


class AnalysisResponse(BaseModel):
    """Token analysis response"""
    success: bool
    analysis: Optional[TokenAnalysis] = None
    error: Optional[str] = None
    processing_time: float
    request_id: str
