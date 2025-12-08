# Git Workflow Guide

This document describes the Git workflow for the DevOps Final Project to ensure proper development practices.

## Branch Strategy

### Main Branch
- `main` - Production-ready code
- Protected branch - requires pull request reviews
- All merges must pass CI/CD tests

### Feature Branches
- Create a new branch for each feature/fix
- Naming convention: `feature/<feature-name>` or `fix/<bug-name>`
- Example: `feature/user-authentication`, `fix/login-bug`

## Workflow Steps

### 1. Creating a Feature Branch

```bash
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Create and switch to a new feature branch
git checkout -b feature/your-feature-name
```

### 2. Making Changes

```bash
# Make your code changes
# Add files to staging
git add .

# Commit with a descriptive message
git commit -m "Add feature: description of your changes"

# Push to remote repository
git push origin feature/your-feature-name
```

### 3. Creating a Pull Request

1. Go to GitHub repository
2. Click "Pull requests" tab
3. Click "New pull request"
4. Select:
   - Base: `main`
   - Compare: `feature/your-feature-name`
5. Fill in the PR template:
   - **Title**: Brief description of changes
   - **Description**: Detailed explanation of what and why
   - **Testing**: How you tested the changes
6. Click "Create pull request"

### 4. Code Review Process

- Wait for CI/CD pipeline to complete
- Address any review comments
- Make additional commits if needed:
  ```bash
  git add .
  git commit -m "Address review comments"
  git push origin feature/your-feature-name
  ```

### 5. Merging

Once approved and CI passes:
1. Ensure branch is up to date with main:
   ```bash
   git checkout feature/your-feature-name
   git pull origin main
   git push origin feature/your-feature-name
   ```
2. Merge the pull request on GitHub
3. Delete the feature branch (on GitHub and locally):
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/your-feature-name
   ```

## CI/CD Pipeline

The CI pipeline automatically runs on:
- Push to `main` branch
- Pull requests to `main` branch

### Pipeline Steps
1. ✅ Checkout code
2. 🐍 Set up Python environment
3. 📦 Install dependencies
4. ✅ Run tests (pytest)
5. 🐳 Build Docker image
6. 📤 Push to Docker Hub (only on merge to main)

## Requirements Checklist

Before creating a PR, ensure:
- [ ] All tests pass locally
- [ ] New features have unit tests (3-5 tests minimum)
- [ ] Code follows project style guidelines
- [ ] Documentation is updated if needed
- [ ] Health check endpoint works (for backend changes)
- [ ] Docker build succeeds

## Example: Complete Feature Development

```bash
# 1. Create feature branch
git checkout main
git pull origin main
git checkout -b feature/add-user-profile

# 2. Develop and test
# ... make changes ...
pytest  # Run tests locally

# 3. Commit changes
git add .
git commit -m "Add user profile endpoint with tests"
git push origin feature/add-user-profile

# 4. Create PR on GitHub
# Wait for review and CI to pass

# 5. After merge, cleanup
git checkout main
git pull origin main
git branch -d feature/add-user-profile
```

## Docker Hub Secrets Configuration

To enable Docker Hub push, configure these secrets in GitHub:
1. Go to Repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token

## Troubleshooting

### CI Tests Failing
```bash
# Run tests locally to debug
PYTHONPATH=. pytest

# Check specific test file
PYTHONPATH=. pytest backend/tests/test_api.py -v
```

### Docker Build Issues
```bash
# Build locally to test
docker build -f backend/Dockerfile -t test-backend .

# Test health check
docker run -d -p 8000:80 test-backend
curl http://localhost:8000/health
```

## Best Practices

1. **Small, Focused PRs**: Keep changes small and focused on one feature
2. **Descriptive Commits**: Write clear commit messages
3. **Test Before Push**: Always run tests locally before pushing
4. **Keep Updated**: Regularly sync your branch with main
5. **Code Review**: Review others' PRs to learn and share knowledge
6. **Documentation**: Update docs when adding features

## Contact

For questions about the workflow, contact the project maintainers.
