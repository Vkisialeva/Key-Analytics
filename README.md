TennisApp
git config --global user.name "Viktoryia Kisialeva"
git config --global user.email "vkisialeva4@gmail.com"

## Branch Strategy

- main: stable and always deployable
- feature/*: used for feature development
- release/*: used for preparing release candidates
- hotfix/*: used for urgent fixes

Rules:
- No direct pushes to main
- All changes must go through pull requests
- CI/CD must pass before merging
- Every merge to main triggers automatic staging deployment