# VideoAI Manager 🎬✨

> **Intelligent video content organization powered by GPT-4 Vision**  
> Automatically analyze, categorize, and organize your video library with AI.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Version](https://img.shields.io/badge/version-v6.0-purple)](CHANGELOG.md)

---

## 🚀 What is VideoAI Manager?

VideoAI Manager is an **open-source automation system** that uses **GPT-4 Vision** and **computer vision** to intelligently process, analyze, and organize video content.

Perfect for content creators, agencies, and teams managing large video libraries.

### ✨ Key Features (V6)

| Feature | Description | Status |
|---------|-------------|--------|
| 🎯 **GPT-4 Vision Analysis** | Semantic understanding of video content (location, action, emotion) | ✅ **NEW** |
| 👤 **Facial Recognition** | Automatic detection and tracking of recurring people | ✅ **NEW** |
| 📚 **Controlled Vocabulary** | Smart categorization system that prevents category explosion | ✅ **NEW** |
| 🔄 **Retroactive Processing** | Re-analyzes old videos when new categories or people are registered | ✅ **NEW** |
| 📊 **Google Drive Integration** | Seamless sync with Google Drive folders | ✅ |
| 📈 **Spreadsheet Inventory** | Auto-updates Google Sheets with video metadata | ✅ |
| 🧹 **Smart Cache Cleanup** | Removes irrelevant faces from social events automatically | ✅ **NEW** |

---

## 🎯 Perfect For

- **Content Creators** managing 100+ videos per month
- **Video Production Teams** organizing raw footage
- **Social Media Managers** curating content libraries
- **Marketing Agencies** handling client video assets
- **E-learning Platforms** categorizing course videos

---

## 📊 How It Works

```
1. Upload videos to Google Drive (INCOMING folder)
   ↓
2. VideoAI extracts 3 strategic frames (20%, 50%, 80%)
   ↓
3. GPT-4 Vision analyzes content semantically
   ↓
4. OpenCV detects and recognizes faces (local, free)
   ↓
5. Smart renaming: 2026-03-17_Action_Location_Shot_Emotion_Xs_People.mp4
   ↓
6. Move to REELS_GENERATED folder
   ↓
7. Update Google Sheets inventory automatically
   ↓
8. Save to history for retroactive processing
```

**Precision:** 95% (GPT-4V semantic analysis)  
**Cost:** ~$0.03 per video  
**Speed:** ~3 minutes per video

---

## 🆕 What's New in V6

### GPT-4 Vision Integration
- **Semantic understanding** (not heuristic rules)
- Detects landscapes (beach, mountain, cycling routes)
- Differentiates movement intensity (walk vs run)
- **95% precision** vs 60% in V5

### Facial Recognition System
- **Automatic detection** of recurring people
- **Local processing** with OpenCV (free, no cloud)
- **Smart notifications**: Only when face appears in ≥2 videos
- **Cache cleanup**: Max 50 unidentified faces, prioritizes recurring ones

### Controlled Vocabulary
- **24 base categories** (8 locations, 9 actions, 7 emotions)
- **Intelligent approval system** (3+ appearances required)
- **Automatic normalization** of synonyms
- **Prevents category explosion** (avoids "Gym_Smartfit_Branch_5")

### Retroactive Processing
- **Re-analyzes frames** with GPT-4V to confirm
- Only updates if new category truly applies
- **Prevents mass errors** (food court ≠ airport)
- Complete history for audit trail

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Google Cloud Service Account (for Drive/Sheets API)
- OpenAI API key (for GPT-4V)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Programaemprender/videoai-manager.git
cd videoai-manager

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

# Process your first video
python src/pipeline_v6.py YOUR_VIDEO_FILE_ID
```

---

## 📖 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** — Complete V6 implementation details
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute
- **[Vocabulary System](docs/vocabulary.md)** — Controlled categorization
- **[Facial Recognition](docs/facial_recognition.md)** — Face detection and tracking
- **[Retroactive Processing](docs/retroactive.md)** — Re-analyzing old videos

---

## 💰 Pricing (Self-Hosted)

| Component | Cost |
|-----------|------|
| OpenCV Facial Recognition | **Free** (local) |
| GPT-4 Vision Analysis | ~$0.03/video |
| Google Drive API | **Free** (within quotas) |
| Google Sheets API | **Free** (within quotas) |

**Example:** Process 100 videos/month = **$3 USD/month**

---

## 🎨 Example Output

**Input:**  
`IMG_3132.MOV` (28 seconds, running in park)

**Output:**  
`2026-03-17_Correr_Parque_TerceraPersona_Esfuerzo_28s_Alejandro.mp4`

**Metadata in Google Sheets:**
| Name | Location | Shot | Description | Action | Emotion | People | Duration | Link |
|------|----------|------|-------------|--------|---------|--------|----------|------|
| 2026-03-17_Correr_Parque... | Park | ThirdPerson | Man running in sunny park | Running | Effort | Alejandro | 28s | [link] |

---

## 📊 V6 Benchmarks

**15 videos processed (real production data):**
- **Precision:** 95% (GPT-4V semantic analysis)
- **Cost:** $0.45 total ($0.03/video)
- **Processing time:** ~3 min/video
- **Facial recognition:** 80% accuracy (when photos available)
- **Categories detected:** 24 base + 4 candidates

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas where we need help:**
- [ ] CLIP integration (free alternative to GPT-4V)
- [ ] Multi-language support
- [ ] Video clip extraction (best moments)
- [ ] Audio transcription integration
- [ ] Web UI dashboard

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🌟 Star History

If this project helps you, please ⭐ star it on GitHub!

---

## 🔗 Links

- **Landing Page:** [videoai.softify.cl](https://videoai.softify.cl)
- **Softify Products:** [softify.cl](https://softify.cl)
- **Issues:** [GitHub Issues](https://github.com/Programaemprender/videoai-manager/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Programaemprender/videoai-manager/discussions)

---

**Built with ❤️ by the Softify Team**
