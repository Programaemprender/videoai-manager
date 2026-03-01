# VideoAI Manager

> AI-powered video library organizer for content creators

**Never lose a clip again.** VideoAI Manager automatically categorizes your video clips using AI, detects recurring people with smart facial recognition, and makes your entire library searchable in seconds.

![VideoAI Manager Demo](https://via.placeholder.com/800x400?text=Demo+Coming+Soon)

## ✨ Features

- 🤖 **AI-Powered Categorization** - Automatically detects actions, locations, emotions, and shot types
- 👥 **Smart Facial Recognition** - Only notifies you about people who appear in 2+ videos (no spam from random extras)
- 🔍 **Instant Search** - Find any clip by action, person, location, or emotion
- 📊 **Google Sheets Integration** - Auto-updates your clip inventory
- 🔗 **Cloud Storage Support** - Works with Google Drive, Dropbox, OneDrive
- 🐳 **Docker Ready** - One-command setup for self-hosting

## 🎯 Who is this for?

- **Content Creators** - YouTubers, TikTokers, Instagramers managing hundreds of clips
- **Video Editors** - Quickly find B-roll and specific shots
- **Marketing Teams** - Organize brand content libraries
- **Agencies** - Manage multiple clients' video assets

## 🚀 Quick Start

### Hosted Service (Recommended)

The easiest way to get started is with our hosted service at [videoai.softify.cl](https://videoai.softify.cl)

**Free tier:** 50 videos/month  
**Creator plan:** $19/month - 500 videos, facial recognition, 50GB storage

### Self-Hosted (Open Source)

**Prerequisites:**
- Python 3.9+
- Docker (optional but recommended)
- OpenAI API key (for advanced features)

**Option 1: Docker (Easiest)**

```bash
docker run -d \
  -v /path/to/videos:/videos \
  -v /path/to/data:/data \
  -p 8000:8000 \
  softify/videoai-manager:latest
```

**Option 2: Manual Install**

```bash
# Clone the repository
git clone https://github.com/Programaemprender/videoai-manager.git
cd videoai-manager

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp .env.example .env
# Edit .env with your settings

# Run the analyzer
python analyze_videos.py --folder /path/to/videos
```

## 📖 How It Works

1. **Point to your video folder** (local or cloud storage)
2. **AI analyzes each video** - Detects objects, actions, emotions
3. **Smart categorization** - Uses your custom vocabulary or generates categories
4. **Facial recognition** - Detects recurring people (opt-in)
5. **Organized library** - Search by any criteria, export to sheets

## 🎬 Example Output

```
Video: IMG_9759.MOV
Renamed: 2026-03-01_Ejercitando_Interior_Selfie_Normal_10s.mp4
Categories:
  Action: Ejercitando
  Location: Interior
  Shot Type: Selfie
  Emotion: Normal
  People Detected: 1 (Kuilen - appears in 3 videos)
```

## 🛠️ Tech Stack

- **AI/ML:** YOLOv5 (object detection), OpenCV (face detection), optional face_recognition
- **Backend:** Python, FastAPI (for hosted service)
- **Storage:** Local filesystem, S3-compatible, Google Drive API
- **Database:** SQLite (self-hosted), PostgreSQL (hosted)

## 📊 Roadmap

### ✅ Completed
- [x] Video analysis with YOLOv5
- [x] Smart facial recognition (recurring people only)
- [x] Google Sheets integration
- [x] Custom vocabulary system

### 🚧 In Progress
- [ ] Web UI for search and preview
- [ ] Docker image
- [ ] Multi-cloud sync (Drive + Dropbox + OneDrive)

### 📅 Planned
- [ ] Voice search ("find clips where I'm running")
- [ ] Auto-generate reels from best clips
- [ ] Integration with Premiere/Final Cut
- [ ] Mobile app (iOS/Android)
- [ ] API for automation

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we need help:**
- 🐛 Bug fixes and testing
- 📝 Documentation improvements
- 🌍 Translations (Spanish, Portuguese, etc.)
- 🎨 UI/UX design for web interface
- 🚀 Performance optimizations

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔒 Privacy & Security

- **Your videos stay yours** - Self-hosted option means zero data leaves your machine
- **Facial data is opt-in** - Recognition only works if you explicitly enable it
- **Encrypted storage** - Hosted service encrypts all data at rest
- **No training on your data** - We never use your videos to train our models

## 💬 Community & Support

- **Discord:** [Join our community](https://discord.gg/videoai-manager)
- **Issues:** [GitHub Issues](https://github.com/Programaemprender/videoai-manager/issues)
- **Email:** support@softify.cl
- **Twitter:** [@softify_ai](https://twitter.com/softify_ai)

## 🌟 Hosted Service

Want zero setup and premium features?

**[Try VideoAI Manager Hosted →](https://videoai.softify.cl)**

- ✅ No installation required
- ✅ Automatic updates
- ✅ Advanced facial recognition
- ✅ Team collaboration
- ✅ Priority support
- ✅ 99.9% uptime SLA

**Pricing:**
- Free: 50 videos/month
- Creator: $19/month
- Team: $49/month
- Agency: $199/month

## 🏆 Built By

Created by [Softify](https://softify.cl) - Makers of tools for modern creators.

**Main Developer:** [Alejandro Chung](https://github.com/your-username) - "El Gladiador Estratega"

## ⭐ Star Us!

If VideoAI Manager helps you stay organized, please star this repo! It helps others discover the project.

---

**Made with ❤️ by creators, for creators.**
