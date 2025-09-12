"""
Configuration settings for Pump.fun Risk Analyzer
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Pump.fun Risk Analyzer"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/pumpfun_analyzer",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Solana
    SOLANA_RPC_URL: str = Field(
        default="https://api.mainnet-beta.solana.com",
        env="SOLANA_RPC_URL"
    )
    SOLANA_WS_URL: str = Field(
        default="wss://api.mainnet-beta.solana.com",
        env="SOLANA_WS_URL"
    )
    SOLANA_COMMITMENT: str = Field(default="confirmed", env="SOLANA_COMMITMENT")
    
    # Pump.fun
    PUMPFUN_API_URL: str = Field(
        default="https://frontend-api.pump.fun",
        env="PUMPFUN_API_URL"
    )
    PUMPFUN_API_KEY: Optional[str] = Field(default=None, env="PUMPFUN_API_KEY")
    
    # Risk Analysis
    RISK_UPDATE_INTERVAL: int = Field(default=300, env="RISK_UPDATE_INTERVAL")  # 5 minutes
    HOLDER_CONCENTRATION_THRESHOLD: float = Field(
        default=0.7, env="HOLDER_CONCENTRATION_THRESHOLD"
    )
    WASH_TRADING_THRESHOLD: float = Field(
        default=0.8, env="WASH_TRADING_THRESHOLD"
    )
    LIQUIDITY_REMOVAL_WINDOW: int = Field(
        default=86400, env="LIQUIDITY_REMOVAL_WINDOW"  # 24 hours
    )
    
    # Alerts
    ALERT_EMAIL_ENABLED: bool = Field(default=True, env="ALERT_EMAIL_ENABLED")
    ALERT_DISCORD_ENABLED: bool = Field(default=True, env="ALERT_DISCORD_ENABLED")
    ALERT_TELEGRAM_ENABLED: bool = Field(default=True, env="ALERT_TELEGRAM_ENABLED")
    
    # Email
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None, env="SMTP_FROM_EMAIL")
    
    # Discord
    DISCORD_WEBHOOK_URL: Optional[str] = Field(default=None, env="DISCORD_WEBHOOK_URL")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")
    
    # Social Media
    TWITTER_API_KEY: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    TWITTER_API_SECRET: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = Field(
        default=None, env="TWITTER_ACCESS_TOKEN_SECRET"
    )
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
