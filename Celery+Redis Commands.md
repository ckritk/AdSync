# Celery + Redis Setup & Commands

## 1. Install Requirements

### For macOS/Linux:
```bash
pip3 install celery redis
```
If you face zsh: no matches found: celery[redis], use this instead:
```
pip install 'celery[redis]' 'celery[beat]'
```
## 2. Start Redis Server
### For macOS (with Homebrew):
```
brew install redis
brew services start redis
```
### For Windows:
Download Redis from: [Link](https://github.com/microsoftarchive/redis/releases)

Run redis-server.exe from the extracted folder.

## 3. Start Celery Worker
```
celery -A celery_app worker --loglevel=info
```
Replace celery_app with the name of your file (e.g., celery_app.py).

## 4. Start Celery Beat Scheduler
```
celery -A celery_app beat --loglevel=info
```
This will trigger tasks.check_and_post based on the schedule defined in beat_schedule.py.








