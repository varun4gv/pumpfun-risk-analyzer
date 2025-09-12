# Pump.fun Risk Analyzer 🛡️

A comprehensive risk analysis and detection system for pump.fun tokens, designed to protect users from rug pulls, honeypots, and other malicious activities.

## ⚠️ Disclaimer

This tool is designed for **educational and protective purposes only**. It helps users identify potentially risky tokens and make informed decisions. This is NOT a trading bot or profit-generating system.

## 🎯 Mission

To create a safer DeFi environment by providing transparent risk analysis and early warning systems for pump.fun tokens.

## ✨ Features

### 🔍 Risk Detection
- **Holder Concentration Analysis** - Identifies tokens with centralized supply
- **Liquidity Monitoring** - Tracks LP token movements and lock status
- **Wash Trading Detection** - Identifies artificial volume patterns
- **Honeypot Detection** - Tests if tokens can be sold
- **Bundler Activity Detection** - Identifies coordinated buying patterns

### 📊 Analytics Dashboard
- Real-time risk scoring
- Historical pattern analysis
- Token holder distribution
- Volume authenticity metrics
- Social sentiment analysis

### 🚨 Alert System
- Real-time risk notifications
- Customizable alert thresholds
- Multi-channel notifications (Discord, Telegram, Email)
- Risk level classification

### 🔒 Security Features
- Read-only analysis (no trading capabilities)
- Transparent methodology
- Open-source detection algorithms
- Community-driven improvements

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Analysis Engine │    │   Dashboard     │
│                 │    │                  │    │                 │
│ • Pump.fun API  │───▶│ • Risk Scoring   │───▶│ • Real-time UI  │
│ • On-chain Data │    │ • Pattern Detect │    │ • Alerts        │
│ • Social Media  │    │ • ML Models      │    │ • Reports       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Solana CLI tools
- Access to Solana RPC endpoint

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pumpfun-risk-analyzer.git
   cd pumpfun-risk-analyzer
   ```

2. **Install dependencies**
   ```bash
   # Frontend
   cd frontend
   npm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the application**
   ```bash
   # Start backend
   cd backend
   python main.py
   
   # Start frontend (in new terminal)
   cd frontend
   npm start
   ```

## 📋 Risk Detection Rules

### 1. Holder Concentration
- **High Risk**: Top 5 holders > 70% of supply
- **Medium Risk**: Top 5 holders 40-70% of supply
- **Low Risk**: Top 5 holders < 40% of supply

### 2. Liquidity Analysis
- **High Risk**: LP removed within 24 hours
- **Medium Risk**: LP removed within 48 hours
- **Low Risk**: LP locked or not removed

### 3. Volume Authenticity
- **High Risk**: >80% volume from <5 addresses
- **Medium Risk**: 60-80% volume from <10 addresses
- **Low Risk**: <60% volume from diverse addresses

### 4. Honeypot Detection
- **High Risk**: Transfer/sell functions revert
- **Low Risk**: All functions work normally

## 🔧 Configuration

### Environment Variables
```env
# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com

# Database
DATABASE_URL=postgresql://user:pass@localhost/pumpfun_analyzer

# API Keys
PUMPFUN_API_KEY=your_api_key
TWITTER_API_KEY=your_twitter_key

# Alert Configuration
DISCORD_WEBHOOK_URL=your_discord_webhook
TELEGRAM_BOT_TOKEN=your_telegram_token
```

## 📊 API Endpoints

### Risk Analysis
```http
GET /api/token/{token_address}/risk
POST /api/token/analyze
GET /api/token/{token_address}/holders
GET /api/token/{token_address}/transactions
```

### Alerts
```http
GET /api/alerts
POST /api/alerts/subscribe
DELETE /api/alerts/{alert_id}
```

## 🧪 Testing

```bash
# Run tests
npm test
python -m pytest backend/tests/

# Run with coverage
npm run test:coverage
python -m pytest --cov=backend backend/tests/
```

## 📈 Roadmap

### Phase 1: Core Detection (Current)
- [x] Basic risk scoring
- [x] Holder concentration analysis
- [x] Liquidity monitoring
- [x] Web dashboard

### Phase 2: Advanced Analytics
- [ ] Machine learning models
- [ ] Social sentiment analysis
- [ ] Historical pattern recognition
- [ ] Mobile app

### Phase 3: Community Features
- [ ] Community reporting system
- [ ] Token verification badges
- [ ] Educational resources
- [ ] API for third-party integrations

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

This tool is for educational and protective purposes only. Users are responsible for their own investment decisions. The developers are not liable for any financial losses.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/yourusername/pumpfun-risk-analyzer/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/pumpfun-risk-analyzer/issues)
- **Discord**: [Community Server](https://discord.gg/your-server)
- **Email**: support@pumpfun-analyzer.com

## 🙏 Acknowledgments

- Solana Foundation for the blockchain infrastructure
- Pump.fun for the trading platform
- Open source community for various libraries and tools

---

**Remember**: This tool is designed to protect users, not to exploit them. Use responsibly and in accordance with all applicable laws and regulations.
