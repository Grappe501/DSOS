# Git Setup and Release Notes

## If repo is not initialized
```powershell
git init
git branch -M main
```

## Recommended `.gitignore`
```gitignore
__pycache__/
*.pyc
*.db
runtime_v5.db
node_modules/
dist/
.env
.venv/
```

## First commit recommendation
```powershell
git add .
git commit -m "feat: add auth, RBAC v1, AllCare branding, and working schedule flow"
git tag v0.6.1-auth-rbac-branding
```

## Push
```powershell
git remote add origin <repo-url>
git push -u origin main
git push origin v0.6.1-auth-rbac-branding
```
