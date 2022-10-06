# ใน proen.cloud
#อย่าลืมเพิ่ม WSGIApplicationGroup %{GLOBAL} ในไฟล์ httpd.conf

import sys
sys.path.insert(0,'/var/www/webroot/ROOT')
from chatbot.chatbot import app as application


