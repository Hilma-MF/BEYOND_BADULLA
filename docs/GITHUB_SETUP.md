# GitHub Setup

This document explains how to initialize the BEYOND BADULLA project with Git and upload it to GitHub.

## 1. Open the Project Directory

Open PowerShell and navigate to the project:

```powershell
cd "D:\Beyond_Badulla_Final_Project_Update\BEYOND_BADULLA"
```

## 2. Initialize Git

```powershell
git init
```

## 3. Check the Files Before Adding Them

```powershell
git status
```

## 4. Add the Project Files

```powershell
git add .
```

## 5. Create the Initial Commit

```powershell
git commit -m "Build BEYOND BADULLA tourism system"
```

## 6. Set the Main Branch

```powershell
git branch -M main
```

## 7. Create the GitHub Repository

Create a new GitHub repository named:

```text
BEYOND_BADULLA
```

## 8. Connect the Local Repository to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/BEYOND_BADULLA.git
```

## 9. Push the Project to GitHub

```powershell
git push -u origin main
```

## 10. Verify the Repository

After pushing the project, open the GitHub repository and verify that the project files and documentation have been uploaded correctly.

## Future Updates

When changes are made to the project:

```powershell
git status
git add .
git commit -m "Describe the changes"
git push
```

## Important

Do not upload the Python virtual environment to GitHub.

The `.gitignore` file should exclude:

```text
venv/
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.vscode/
```

Do not upload passwords, secret keys, API keys, or other sensitive credentials to GitHub.
