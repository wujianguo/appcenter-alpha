# appcenter-alpha

[![Django CI](https://github.com/wujianguo/appcenter-alpha/actions/workflows/django.yml/badge.svg)](https://github.com/wujianguo/appcenter-alpha/actions/workflows/django.yml)
[![codecov](https://codecov.io/gh/wujianguo/appcenter-alpha/branch/main/graph/badge.svg?token=LBDG3XLKLC)](https://codecov.io/gh/wujianguo/appcenter-alpha)

[API Documentation](https://app.swaggerhub.com/apis-docs/wujianguo/appcenter/1.0.0)

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir var
mkdir var/log
uwsgi --ini appcenter.ini
uwsgi --stop /tmp/appcenter-master.pid
```