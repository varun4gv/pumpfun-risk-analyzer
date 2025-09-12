"""
Risk analysis service for pump.fun tokens
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

from ..config import settings
from ..models import (
    TokenAnalysis, TokenRisk, RiskLevel, HolderInfo, 
    LiquidityInfo, VolumeInfo, SocialInfo, RiskFactor
)
from .solana_service import SolanaService
from .social_service import SocialService
from .database_service import DatabaseService


class RiskAnalyzer:
    """Main risk analysis service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.solana_service = SolanaService()
        self.social_service = SocialService()
        self.db_service = DatabaseService()
        self.monitoring_active = False
        
        # Risk weights
        self.risk_weights = {
            "holder_concentration": 0.25,
            "liquidity_security": 0.20,
            "volume_authenticity": 0.15,
            "social_credibility": 0.10,
            "contract_security": 0.15,
            "price_stability": 0.10,
            "trading_patterns": 0.05
        }
    
    async def analyze_token(self, token_address: str) -> TokenAnalysis:
        """Perform comprehensive risk analysis on a token"""
        self.logger.info(f"Starting analysis for token: {token_address}")
        start_time = datetime.now()
        
        try:
            # Get basic token info
            token_info = await self.solana_service.get_token_info(token_address)
            
            # Analyze different aspects
            holders = await self._analyze_holders(token_address)
            liquidity = await self._analyze_liquidity(token_address)
            volume = await self._analyze_volume(token_address)
            social = await self._analyze_social(token_address)
            
            # Calculate risk factors
            risk_factors = await self._calculate_risk_factors(
                token_address, holders, liquidity, volume, social
            )
            
            # Calculate overall risk score
            risk_score, risk_level = self._calculate_risk_score(risk_factors)
            
            # Create analysis result
            analysis = TokenAnalysis(
                token_address=token_address,
                token_name=token_info.get("name"),
                token_symbol=token_info.get("symbol"),
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=self._calculate_confidence(risk_factors),
                holders=holders,
                liquidity=liquidity,
                volume=volume,
                social=social,
                risk_factors=risk_factors,
                analysis_timestamp=datetime.now(),
                created_at=datetime.now()
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Analysis completed for {token_address} in {processing_time:.2f}s"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing token {token_address}: {e}")
            raise
    
    async def _analyze_holders(self, token_address: str) -> List[HolderInfo]:
        """Analyze token holder distribution"""
        try:
            holders_data = await self.solana_service.get_token_holders(token_address)
            holders = []
            
            total_supply = sum(h["balance"] for h in holders_data)
            
            for holder in holders_data:
                percentage = (holder["balance"] / total_supply) * 100 if total_supply > 0 else 0
                
                holders.append(HolderInfo(
                    address=holder["address"],
                    balance=holder["balance"],
                    percentage=percentage,
                    is_contract=await self.solana_service.is_contract_address(holder["address"]),
                    first_seen=holder.get("first_seen"),
                    last_activity=holder.get("last_activity")
                ))
            
            # Sort by balance descending
            holders.sort(key=lambda x: x.balance, reverse=True)
            return holders
            
        except Exception as e:
            self.logger.error(f"Error analyzing holders for {token_address}: {e}")
            return []
    
    async def _analyze_liquidity(self, token_address: str) -> LiquidityInfo:
        """Analyze liquidity security"""
        try:
            liquidity_data = await self.solana_service.get_liquidity_info(token_address)
            
            return LiquidityInfo(
                total_liquidity=liquidity_data.get("total_liquidity", 0),
                locked_liquidity=liquidity_data.get("locked_liquidity", 0),
                locked_percentage=liquidity_data.get("locked_percentage", 0),
                lock_duration=liquidity_data.get("lock_duration"),
                lock_expiry=liquidity_data.get("lock_expiry"),
                lp_token_holders=liquidity_data.get("lp_token_holders", [])
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing liquidity for {token_address}: {e}")
            return LiquidityInfo(
                total_liquidity=0,
                locked_liquidity=0,
                locked_percentage=0,
                lp_token_holders=[]
            )
    
    async def _analyze_volume(self, token_address: str) -> VolumeInfo:
        """Analyze trading volume authenticity"""
        try:
            volume_data = await self.solana_service.get_volume_analysis(token_address)
            
            return VolumeInfo(
                total_volume_24h=volume_data.get("total_volume_24h", 0),
                unique_traders=volume_data.get("unique_traders", 0),
                wash_trading_score=volume_data.get("wash_trading_score", 0),
                volume_authenticity=volume_data.get("volume_authenticity", 0),
                top_traders_percentage=volume_data.get("top_traders_percentage", 0)
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing volume for {token_address}: {e}")
            return VolumeInfo(
                total_volume_24h=0,
                unique_traders=0,
                wash_trading_score=0,
                volume_authenticity=0,
                top_traders_percentage=0
            )
    
    async def _analyze_social(self, token_address: str) -> SocialInfo:
        """Analyze social media presence and credibility"""
        try:
            social_data = await self.social_service.analyze_token_social(token_address)
            
            return SocialInfo(
                twitter_mentions=social_data.get("twitter_mentions", 0),
                telegram_members=social_data.get("telegram_members", 0),
                discord_members=social_data.get("discord_members", 0),
                website_exists=social_data.get("website_exists", False),
                domain_age_days=social_data.get("domain_age_days"),
                social_sentiment=social_data.get("social_sentiment")
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing social for {token_address}: {e}")
            return SocialInfo()
    
    async def _calculate_risk_factors(
        self, 
        token_address: str, 
        holders: List[HolderInfo], 
        liquidity: LiquidityInfo, 
        volume: VolumeInfo, 
        social: SocialInfo
    ) -> Dict[str, RiskFactor]:
        """Calculate individual risk factors"""
        risk_factors = {}
        
        # Holder concentration risk
        holder_concentration = self._calculate_holder_concentration_risk(holders)
        risk_factors["holder_concentration"] = holder_concentration
        
        # Liquidity security risk
        liquidity_security = self._calculate_liquidity_security_risk(liquidity)
        risk_factors["liquidity_security"] = liquidity_security
        
        # Volume authenticity risk
        volume_authenticity = self._calculate_volume_authenticity_risk(volume)
        risk_factors["volume_authenticity"] = volume_authenticity
        
        # Social credibility risk
        social_credibility = self._calculate_social_credibility_risk(social)
        risk_factors["social_credibility"] = social_credibility
        
        # Contract security risk
        contract_security = await self._calculate_contract_security_risk(token_address)
        risk_factors["contract_security"] = contract_security
        
        # Price stability risk
        price_stability = await self._calculate_price_stability_risk(token_address)
        risk_factors["price_stability"] = price_stability
        
        # Trading patterns risk
        trading_patterns = await self._calculate_trading_patterns_risk(token_address)
        risk_factors["trading_patterns"] = trading_patterns
        
        return risk_factors
    
    def _calculate_holder_concentration_risk(self, holders: List[HolderInfo]) -> RiskFactor:
        """Calculate holder concentration risk"""
        if not holders:
            return RiskFactor(
                name="holder_concentration",
                description="No holder data available",
                score=1.0,
                weight=self.risk_weights["holder_concentration"],
                evidence=["No holder data found"]
            )
        
        # Calculate Gini coefficient
        balances = [h.balance for h in holders]
        gini_coefficient = self._calculate_gini_coefficient(balances)
        
        # Top 5 holders percentage
        top_5_percentage = sum(h.percentage for h in holders[:5])
        
        # Risk score based on concentration
        if top_5_percentage > 80:
            score = 1.0
            level = "CRITICAL"
        elif top_5_percentage > 60:
            score = 0.8
            level = "HIGH"
        elif top_5_percentage > 40:
            score = 0.6
            level = "MEDIUM"
        else:
            score = 0.3
            level = "LOW"
        
        evidence = [
            f"Top 5 holders control {top_5_percentage:.1f}% of supply",
            f"Gini coefficient: {gini_coefficient:.3f}",
            f"Total holders: {len(holders)}"
        ]
        
        recommendation = (
            "Consider diversifying token distribution" if score > 0.6
            else "Holder distribution looks healthy"
        )
        
        return RiskFactor(
            name="holder_concentration",
            description=f"Token holder concentration analysis ({level})",
            score=score,
            weight=self.risk_weights["holder_concentration"],
            evidence=evidence,
            recommendation=recommendation
        )
    
    def _calculate_liquidity_security_risk(self, liquidity: LiquidityInfo) -> RiskFactor:
        """Calculate liquidity security risk"""
        if liquidity.total_liquidity == 0:
            return RiskFactor(
                name="liquidity_security",
                description="No liquidity data available",
                score=1.0,
                weight=self.risk_weights["liquidity_security"],
                evidence=["No liquidity found"]
            )
        
        # Risk based on locked percentage
        locked_percentage = liquidity.locked_percentage
        
        if locked_percentage < 20:
            score = 1.0
            level = "CRITICAL"
        elif locked_percentage < 50:
            score = 0.8
            level = "HIGH"
        elif locked_percentage < 80:
            score = 0.5
            level = "MEDIUM"
        else:
            score = 0.2
            level = "LOW"
        
        evidence = [
            f"Total liquidity: {liquidity.total_liquidity:.2f} SOL",
            f"Locked percentage: {locked_percentage:.1f}%",
            f"LP token holders: {len(liquidity.lp_token_holders)}"
        ]
        
        if liquidity.lock_expiry:
            evidence.append(f"Lock expires: {liquidity.lock_expiry}")
        
        recommendation = (
            "Ensure liquidity is properly locked" if score > 0.6
            else "Liquidity security looks good"
        )
        
        return RiskFactor(
            name="liquidity_security",
            description=f"Liquidity security analysis ({level})",
            score=score,
            weight=self.risk_weights["liquidity_security"],
            evidence=evidence,
            recommendation=recommendation
        )
    
    def _calculate_volume_authenticity_risk(self, volume: VolumeInfo) -> RiskFactor:
        """Calculate volume authenticity risk"""
        wash_trading_score = volume.wash_trading_score
        
        if wash_trading_score > 0.8:
            score = 1.0
            level = "CRITICAL"
        elif wash_trading_score > 0.6:
            score = 0.8
            level = "HIGH"
        elif wash_trading_score > 0.4:
            score = 0.5
            level = "MEDIUM"
        else:
            score = 0.2
            level = "LOW"
        
        evidence = [
            f"24h volume: {volume.total_volume_24h:.2f} SOL",
            f"Unique traders: {volume.unique_traders}",
            f"Wash trading score: {wash_trading_score:.3f}",
            f"Volume authenticity: {volume.volume_authenticity:.3f}"
        ]
        
        recommendation = (
            "Volume appears artificial - exercise caution" if score > 0.6
            else "Volume appears organic"
        )
        
        return RiskFactor(
            name="volume_authenticity",
            description=f"Volume authenticity analysis ({level})",
            score=score,
            weight=self.risk_weights["volume_authenticity"],
            evidence=evidence,
            recommendation=recommendation
        )
    
    def _calculate_social_credibility_risk(self, social: SocialInfo) -> RiskFactor:
        """Calculate social credibility risk"""
        # Simple scoring based on social presence
        social_score = 0
        
        if social.twitter_mentions > 100:
            social_score += 0.3
        elif social.twitter_mentions > 10:
            social_score += 0.1
        
        if social.telegram_members > 1000:
            social_score += 0.3
        elif social.telegram_members > 100:
            social_score += 0.1
        
        if social.website_exists:
            social_score += 0.2
        
        if social.domain_age_days and social.domain_age_days > 30:
            social_score += 0.2
        
        # Convert to risk score (higher social score = lower risk)
        score = max(0, 1 - social_score)
        
        if score > 0.8:
            level = "HIGH"
        elif score > 0.5:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        evidence = [
            f"Twitter mentions: {social.twitter_mentions}",
            f"Telegram members: {social.telegram_members}",
            f"Website exists: {social.website_exists}",
            f"Domain age: {social.domain_age_days or 'Unknown'} days"
        ]
        
        recommendation = (
            "Build stronger social media presence" if score > 0.6
            else "Social credibility looks good"
        )
        
        return RiskFactor(
            name="social_credibility",
            description=f"Social credibility analysis ({level})",
            score=score,
            weight=self.risk_weights["social_credibility"],
            evidence=evidence,
            recommendation=recommendation
        )
    
    async def _calculate_contract_security_risk(self, token_address: str) -> RiskFactor:
        """Calculate contract security risk"""
        try:
            # Check for common security issues
            security_issues = await self.solana_service.check_contract_security(token_address)
            
            # Count issues
            issue_count = len(security_issues)
            
            if issue_count > 5:
                score = 1.0
                level = "CRITICAL"
            elif issue_count > 3:
                score = 0.8
                level = "HIGH"
            elif issue_count > 1:
                score = 0.5
                level = "MEDIUM"
            else:
                score = 0.2
                level = "LOW"
            
            evidence = security_issues if security_issues else ["No security issues detected"]
            
            recommendation = (
                "Address security concerns before trading" if score > 0.6
                else "Contract security looks good"
            )
            
            return RiskFactor(
                name="contract_security",
                description=f"Contract security analysis ({level})",
                score=score,
                weight=self.risk_weights["contract_security"],
                evidence=evidence,
                recommendation=recommendation
            )
            
        except Exception as e:
            self.logger.error(f"Error checking contract security: {e}")
            return RiskFactor(
                name="contract_security",
                description="Contract security analysis failed",
                score=0.5,
                weight=self.risk_weights["contract_security"],
                evidence=["Unable to analyze contract security"]
            )
    
    async def _calculate_price_stability_risk(self, token_address: str) -> RiskFactor:
        """Calculate price stability risk"""
        try:
            price_data = await self.solana_service.get_price_history(token_address)
            
            if not price_data or len(price_data) < 2:
                return RiskFactor(
                    name="price_stability",
                    description="Insufficient price data",
                    score=0.5,
                    weight=self.risk_weights["price_stability"],
                    evidence=["Not enough price history"]
                )
            
            # Calculate volatility
            prices = [p["price"] for p in price_data]
            volatility = np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 1.0
            
            if volatility > 0.5:
                score = 1.0
                level = "CRITICAL"
            elif volatility > 0.3:
                score = 0.8
                level = "HIGH"
            elif volatility > 0.1:
                score = 0.5
                level = "MEDIUM"
            else:
                score = 0.2
                level = "LOW"
            
            evidence = [
                f"Price volatility: {volatility:.3f}",
                f"Price range: {min(prices):.6f} - {max(prices):.6f}",
                f"Data points: {len(price_data)}"
            ]
            
            recommendation = (
                "High volatility - trade with caution" if score > 0.6
                else "Price appears stable"
            )
            
            return RiskFactor(
                name="price_stability",
                description=f"Price stability analysis ({level})",
                score=score,
                weight=self.risk_weights["price_stability"],
                evidence=evidence,
                recommendation=recommendation
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating price stability: {e}")
            return RiskFactor(
                name="price_stability",
                description="Price stability analysis failed",
                score=0.5,
                weight=self.risk_weights["price_stability"],
                evidence=["Unable to analyze price stability"]
            )
    
    async def _calculate_trading_patterns_risk(self, token_address: str) -> RiskFactor:
        """Calculate trading patterns risk"""
        try:
            trading_data = await self.solana_service.get_trading_patterns(token_address)
            
            # Analyze for suspicious patterns
            suspicious_patterns = []
            
            # Check for rapid trading
            if trading_data.get("rapid_trading", False):
                suspicious_patterns.append("Rapid trading detected")
            
            # Check for coordinated buying
            if trading_data.get("coordinated_buying", False):
                suspicious_patterns.append("Coordinated buying detected")
            
            # Check for wash trading
            if trading_data.get("wash_trading", False):
                suspicious_patterns.append("Wash trading detected")
            
            issue_count = len(suspicious_patterns)
            
            if issue_count > 2:
                score = 1.0
                level = "CRITICAL"
            elif issue_count > 1:
                score = 0.8
                level = "HIGH"
            elif issue_count > 0:
                score = 0.5
                level = "MEDIUM"
            else:
                score = 0.2
                level = "LOW"
            
            evidence = suspicious_patterns if suspicious_patterns else ["No suspicious patterns detected"]
            
            recommendation = (
                "Suspicious trading patterns detected" if score > 0.6
                else "Trading patterns appear normal"
            )
            
            return RiskFactor(
                name="trading_patterns",
                description=f"Trading patterns analysis ({level})",
                score=score,
                weight=self.risk_weights["trading_patterns"],
                evidence=evidence,
                recommendation=recommendation
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing trading patterns: {e}")
            return RiskFactor(
                name="trading_patterns",
                description="Trading patterns analysis failed",
                score=0.5,
                weight=self.risk_weights["trading_patterns"],
                evidence=["Unable to analyze trading patterns"]
            )
    
    def _calculate_risk_score(self, risk_factors: Dict[str, RiskFactor]) -> Tuple[float, RiskLevel]:
        """Calculate overall risk score and level"""
        total_score = 0
        total_weight = 0
        
        for factor in risk_factors.values():
            total_score += factor.score * factor.weight
            total_weight += factor.weight
        
        # Normalize score
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0.5
        
        # Determine risk level
        if normalized_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif normalized_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif normalized_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return normalized_score, risk_level
    
    def _calculate_confidence(self, risk_factors: Dict[str, RiskFactor]) -> float:
        """Calculate confidence in the risk assessment"""
        # Simple confidence calculation based on data availability
        confidence_factors = []
        
        for factor in risk_factors.values():
            if factor.evidence and len(factor.evidence) > 0:
                confidence_factors.append(1.0)
            else:
                confidence_factors.append(0.5)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for inequality measurement"""
        if not values or len(values) < 2:
            return 0.0
        
        # Sort values
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Calculate Gini coefficient
        cumsum = 0
        for i, value in enumerate(sorted_values):
            cumsum += value * (n - i)
        
        return (2 * cumsum) / (n * sum(sorted_values)) - (n + 1) / n
    
    async def start_monitoring(self):
        """Start continuous monitoring of tokens"""
        self.monitoring_active = True
        self.logger.info("Started token monitoring")
        
        while self.monitoring_active:
            try:
                # Get tokens to monitor
                tokens_to_monitor = await self.db_service.get_tokens_to_monitor()
                
                for token_address in tokens_to_monitor:
                    try:
                        # Perform quick risk check
                        risk = await self.quick_risk_check(token_address)
                        
                        # Store risk data
                        await self.db_service.store_risk_data(token_address, risk)
                        
                        # Check for alerts
                        await self.check_for_alerts(token_address, risk)
                        
                    except Exception as e:
                        self.logger.error(f"Error monitoring token {token_address}: {e}")
                
                # Wait before next check
                await asyncio.sleep(settings.RISK_UPDATE_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopped token monitoring")
    
    async def quick_risk_check(self, token_address: str) -> TokenRisk:
        """Perform a quick risk check (lighter than full analysis)"""
        try:
            # Get basic data
            holders = await self._analyze_holders(token_address)
            liquidity = await self._analyze_liquidity(token_address)
            
            # Calculate basic risk factors
            holder_concentration = self._calculate_holder_concentration_risk(holders)
            liquidity_security = self._calculate_liquidity_security_risk(liquidity)
            
            # Calculate quick risk score
            risk_score = (holder_concentration.score * holder_concentration.weight + 
                         liquidity_security.score * liquidity_security.weight)
            
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.4:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            return TokenRisk(
                token_address=token_address,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=0.7,  # Lower confidence for quick checks
                factors={
                    "holder_concentration": holder_concentration.dict(),
                    "liquidity_security": liquidity_security.dict()
                },
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in quick risk check for {token_address}: {e}")
            return TokenRisk(
                token_address=token_address,
                risk_level=RiskLevel.MEDIUM,
                risk_score=0.5,
                confidence=0.0,
                factors={"error": str(e)},
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
    
    async def check_for_alerts(self, token_address: str, risk: TokenRisk):
        """Check if risk data triggers any alerts"""
        try:
            # Check for high risk alerts
            if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self.db_service.create_alert(
                    token_address=token_address,
                    alert_type="high_risk",
                    risk_level=risk.risk_level,
                    title=f"High Risk Detected: {token_address}",
                    description=f"Token {token_address} has been flagged as {risk.risk_level.value} risk",
                    severity=5 if risk.risk_level == RiskLevel.CRITICAL else 4
                )
            
            # Check for specific risk factors
            factors = risk.factors
            
            if "holder_concentration" in factors:
                holder_factor = factors["holder_concentration"]
                if holder_factor.get("score", 0) > 0.8:
                    await self.db_service.create_alert(
                        token_address=token_address,
                        alert_type="holder_concentration",
                        risk_level=RiskLevel.HIGH,
                        title=f"High Holder Concentration: {token_address}",
                        description=f"Token {token_address} has high holder concentration",
                        severity=4
                    )
            
            if "liquidity_security" in factors:
                liquidity_factor = factors["liquidity_security"]
                if liquidity_factor.get("score", 0) > 0.8:
                    await self.db_service.create_alert(
                        token_address=token_address,
                        alert_type="liquidity_removal",
                        risk_level=RiskLevel.HIGH,
                        title=f"Liquidity Security Risk: {token_address}",
                        description=f"Token {token_address} has liquidity security concerns",
                        severity=4
                    )
            
        except Exception as e:
            self.logger.error(f"Error checking alerts for {token_address}: {e}")
