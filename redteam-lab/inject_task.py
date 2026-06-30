import sys
import os
sys.path.append(os.path.join(os.getcwd(), "central-server"))
from database.db import SessionLocal, Task
db = SessionLocal()
t = Task(campaign_id='0a1bd491-54a2-47e8-bf71-3fa64df7854e', module='credentials.env_secret_scan', status='completed', result={"findings": ["Found AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE in /etc/environment"]})
db.add(t)
db.commit()
db.refresh(t)
print(t.id)
