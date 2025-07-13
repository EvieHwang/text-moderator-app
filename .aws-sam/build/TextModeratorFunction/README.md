# 🛡️ Text Moderator

A privacy-focused, AI-powered text toxicity analysis tool built with Flask and powered by Duc Haba's Friendly Text Moderation API.

## ✨ Features

- **🔒 Privacy First**: Anonymous usage, no data logging or storage
- **🎨 Modern UI**: Beautiful Atom One Dark theme
- **⚡ Real-time Analysis**: Instant toxicity detection across multiple categories
- **🛡️ Rate Limited**: 20 requests per hour to prevent abuse
- **📱 Responsive**: Works on desktop and mobile
- **🚫 No Registration**: No accounts or personal info required

## 🔍 Analysis Categories

- Harassment & Threatening
- Hate Speech & Threatening
- Violence & Graphic Violence
- Sexual Content & Minors
- Self-Harm, Instructions & Intent

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- HuggingFace account (for API access)

### Local Development

1. **Clone the repository**
   git clone <your-repo-url>
   cd text-moderator-app

2. **Set up virtual environment**
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**
   pip install -r requirements.txt

4. **Configure environment**
   cp .env.example .env
   # Edit .env with your HuggingFace token

5. **Run the application**
   python backend/app.py

6. **Open in browser**
   http://localhost:8000

## 🔐 Environment Variables

Create a .env file:

HUGGINGFACE_TOKEN=your_huggingface_token_here

## 🏗️ Project Structure

text-moderator-app/
├── backend/
│   ├── app.py              # Flask application
│   └── templates/
│       └── index.html      # Frontend interface
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
└── README.md             # This file

## 🌐 Deployment

### AWS Lambda + API Gateway

Ready for serverless deployment to AWS. See deployment guide for detailed instructions.

### Other Platforms

- **Heroku**: One-click deployment ready
- **Vercel**: Serverless function compatible
- **Railway**: Container deployment ready

## 🔒 Privacy & Security

- **No Data Storage**: Text is analyzed in real-time and immediately discarded
- **No Logging**: User inputs are never logged or stored
- **Anonymous Usage**: No user accounts or personal information collected
- **Rate Limited**: Prevents API abuse with 20 requests/hour limit
- **Secure**: API keys properly protected and never exposed to client

## 🎯 Use Cases

- **Content Moderation**: Review user-generated content
- **Social Media**: Pre-screen posts and comments
- **Education**: Teach about AI and text analysis
- **Development**: Test moderation algorithms
- **Research**: Analyze text toxicity patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Duc Haba** - For the Friendly Text Moderation API
- **HuggingFace** - For hosting the AI model
- **Flask** - For the web framework

## 📞 Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

---

**Built with ❤️ for safer online communities**
