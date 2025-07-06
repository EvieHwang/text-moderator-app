🛡️ Text Moderator
A privacy-focused, AI-powered text toxicity analysis tool built with Flask and powered by Duc Haba's Friendly Text Moderation API.
✨ Features

🔒 Privacy First: Anonymous usage, no data logging or storage
🎨 Modern UI: Beautiful Atom One Dark theme
⚡ Real-time Analysis: Instant toxicity detection across multiple categories
🛡️ Rate Limited: 20 requests per hour to prevent abuse
📱 Responsive: Works on desktop and mobile
🚫 No Registration: No accounts or personal info required

🔍 Analysis Categories

Harassment & Threatening
Hate Speech & Threatening
Violence & Graphic Violence
Sexual Content & Minors
Self-Harm, Instructions & Intent

🚀 Quick Start
Prerequisites

Python 3.9+
HuggingFace account (for API access)

Local Development

Clone the repository
bashgit clone <your-repo-url>
cd text-moderator-app

Set up virtual environment
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies
bashpip install -r requirements.txt

Configure environment
bashcp .env.example .env
# Edit .env with your HuggingFace token

Run the application
bashpython backend/app.py

Open in browser
http://localhost:8000


🔐 Environment Variables
Create a .env file:
envHUGGINGFACE_TOKEN=your_huggingface_token_here
🏗️ Project Structure
text-moderator-app/
├── backend/
│   ├── app.py              # Flask application
│   └── templates/
│       └── index.html      # Frontend interface
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
└── README.md             # This file
🌐 Deployment
AWS Lambda + API Gateway
Ready for serverless deployment to AWS. See deployment guide for detailed instructions.
Other Platforms

Heroku: One-click deployment ready
Vercel: Serverless function compatible
Railway: Container deployment ready

🔒 Privacy & Security

No Data Storage: Text is analyzed in real-time and immediately discarded
No Logging: User inputs are never logged or stored
Anonymous Usage: No user accounts or personal information collected
Rate Limited: Prevents API abuse with 20 requests/hour limit
Secure: API keys properly protected and never exposed to client

🎯 Use Cases

Content Moderation: Review user-generated content
Social Media: Pre-screen posts and comments
Education: Teach about AI and text analysis
Development: Test moderation algorithms
Research: Analyze text toxicity patterns

🤝 Contributing

Fork the repository
Create a feature branch
Make your changes
Add tests if applicable
Submit a pull request

📄 License
MIT License - see LICENSE file for details.
🙏 Acknowledgments

Duc Haba - For the Friendly Text Moderation API
HuggingFace - For hosting the AI model
Flask - For the web framework

📞 Support
For issues or questions:

Check existing GitHub issues
Create a new issue with detailed description
Include error messages and steps to reproduce


Built with ❤️ for safer online communities
The main changes I made:

Removed the escaped newline characters (\n) that were showing up in the raw text
Fixed the backslash in the Windows path (venv\Scripts\activate)
Ensured proper formatting and spacing throughout
Made the content clean and readable
