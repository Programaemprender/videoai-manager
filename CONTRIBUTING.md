# Contributing to VideoAI Manager

Thank you for your interest in contributing! 🎉

## Ways to Contribute

- 🐛 **Report bugs** - Open an issue with reproduction steps
- 💡 **Suggest features** - Share your ideas in Discussions
- 📝 **Improve docs** - Fix typos, add examples, translate
- 🔧 **Submit code** - Fix bugs or implement features

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/videoai-manager.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "feat: add awesome feature"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Testing

Before submitting a PR, test your changes:

```bash
# Run with test videos
python analyze_videos.py --folder ./test_videos --dry-run

# Check for errors
python -m pytest tests/
```

## Need Help?

- Join our [Discord](https://discord.gg/videoai-manager)
- Ask in [Discussions](https://github.com/softify-ai/videoai-manager/discussions)
- Email: support@softify.cl

## Code of Conduct

Be respectful and inclusive. We're building this together! 🤝
