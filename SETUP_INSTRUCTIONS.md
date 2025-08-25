# 🔧 Repository Setup Instructions

This document contains the steps to complete the GitHub repository setup after initial creation.

## Step 1: Update Repository URLs

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` in the following files with your actual GitHub repository information:

### Files to Update:
- `setup.py` (lines 25, 27-31)
- `README.md` (any GitHub links)
- `.github/workflows/*.yml` (if any contain hardcoded URLs)

### Example Replacements:
```
YOUR_USERNAME → YourGitHubUsername
YOUR_REPO_NAME → yss-community-strategies
```

## Step 2: Configure GitHub Repository Settings

### Branch Protection Rules
1. Go to **Settings** → **Branches**
2. Add rule for `main` branch:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### GitHub Actions Secrets
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these repository secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token (for automated publishing)
   - `TEST_PYPI_API_TOKEN`: Test PyPI token (optional, for testing)

### Enable Repository Features
1. **Settings** → **General**:
   - ✅ Issues
   - ✅ Pull requests  
   - ✅ Discussions
   - ✅ Projects
   - ✅ Wiki

## Step 3: Test the Infrastructure

### Validate Workflow Files
```bash
# Test validation scripts locally
python scripts/validate_strategy_metadata.py
python scripts/check_strategy_requirements.py
python scripts/benchmark_strategies.py --spins 100
```

### Test Package Installation
```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/ -v
```

## Step 4: Create First Release

### Tag and Release
```bash
git tag v1.0.0
git push origin v1.0.0
```

### GitHub Release
1. Go to **Releases** → **Create a new release**
2. Tag: `v1.0.0`
3. Title: `YSS Community Strategies v1.0.0`
4. Description: Initial release with community infrastructure

## Step 5: Community Setup

### Issue Templates
- Strategy submissions will use `.github/ISSUE_TEMPLATE/strategy-submission.md`
- Bug reports will use `.github/ISSUE_TEMPLATE/bug-report.md`

### PR Template
- All pull requests will use `.github/PULL_REQUEST_TEMPLATE.md`

### Documentation
- Main guide: `docs/CONTRIBUTING.md`
- Strategy template: `docs/STRATEGY_TEMPLATE.py`

## Step 6: Invite Contributors

### Add Collaborators
1. **Settings** → **Collaborators and teams**
2. Add maintainers with appropriate permissions

### Community Guidelines
Consider adding:
- Code of Conduct
- Security Policy
- Governance Model

## Step 7: Post-Setup Tasks

### Update Package Metadata
- Verify `pyproject.toml` settings
- Test PyPI publishing workflow
- Update documentation links

### Marketing
- Announce in YSS community
- Create documentation site
- Add to package indexes

---

🎉 **Once completed, delete this file and you're ready for community contributions!**
