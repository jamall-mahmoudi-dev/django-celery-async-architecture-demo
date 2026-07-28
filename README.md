#  Celery + Django REST Framework + Redis + smtp4dev + PostgreSQL + test Performance

یک پروژه آموزشی و عملی برای نمایش معماری **Async Task Processing** در Django است.

در این پروژه یک سناریوی واقعی پیاده‌سازی شده است:

کاربر از طریق API ثبت‌نام می‌کند، Django درخواست را سریع پاسخ می‌دهد، سپس ارسال ایمیل بدون منتظر نگه داشتن کاربر در پس‌زمینه توسط **Celery Worker** انجام می‌شود.

در این معماری از ابزارهای واقعی Production استفاده شده است:

* Django REST Framework برای ساخت API
* Nginx به عنوان Reverse Proxy
* Gunicorn برای اجرای Django در محیط Production
* PostgreSQL برای ذخیره اطلاعات
* Redis به عنوان Message Broker
* Celery برای اجرای Taskهای پس‌زمینه
* Celery Beat برای اجرای Taskهای زمان‌بندی شده
* smtp4dev برای شبیه‌سازی سرویس ایمیل
* Flower برای مانیتورینگ Celery
* Locust برای تست فشار و Load Testing

---

#  هدف پروژه

هدف این پروژه آموزش چرخه کامل یک درخواست Async در Django است:

```
User Request
      |
      ▼
 Django API
      |
      |
      ├── ذخیره اطلاعات در PostgreSQL
      |
      └── ارسال Task به Redis
                    |
                    ▼
              Celery Worker
                    |
                    ▼
              ارسال Email
                    |
                    ▼
                smtp4dev
```

کاربر نباید منتظر عملیات سنگین مثل ارسال ایمیل بماند.

Django فقط Task را ایجاد می‌کند و Worker در پس‌زمینه کار را انجام می‌دهد.

---

#  معماری سیستم

```
                  Browser / curl / Locust

                          |
                          |
                          ▼

                    Nginx :80

                          |
                          |
                          ▼

                     Gunicorn

                          |
                          |
                          ▼

              Django REST Framework

                    /              \

                   /                \

                  ▼                  ▼


           PostgreSQL             Redis

        Users + TaskResult       Message Broker

                                      |
                                      |
                                      ▼

                              Celery Worker

                                      |
                                      |
                                      ▼

                                smtp4dev


                                      ▲

                                      |

                              Celery Beat


                                      |

                              Periodic Tasks



                         Flower :5555

                      Celery Monitoring

```

---

#  جریان کامل یک درخواست

## 1. ثبت نام کاربر

کاربر درخواست زیر را ارسال می‌کند:

```
POST /api/register/
```

مثال:

```json
{
 "username": "Jamall",
 "email": "devops523@gmali.com",
 "password": "12345678"
}
```

---

## 2. Django درخواست را پردازش می‌کند

Django:

* اطلاعات را Validate می‌کند
* User را در PostgreSQL ذخیره می‌کند
* یک Celery Task ایجاد می‌کند

مثلا:

```
send_welcome_email()
```

---

## 3. ارسال Task به Redis

Redis مانند یک صف پیام عمل می‌کند:

```
Redis Queue


[
   send_welcome_email(task_id=123)
]

```

---

## 4. Celery Worker Task را دریافت می‌کند

Worker:

```
Receive Task

        |

Execute Business Logic

        |

Send Email

```

---

## 5. ارسال ایمیل

برای محیط Development از smtp4dev استفاده شده است.

ایمیل واقعی ارسال نمی‌شود.

در عوض داخل Web UI نمایش داده می‌شود.

آدرس:

```
http://localhost:5000
```

---

## 6. ذخیره نتیجه Task

نتیجه اجرای Task در PostgreSQL ذخیره می‌شود:

```
TaskResult

status = SUCCESS
```

این اطلاعات توسط:

* API
* Flower
* سیستم مانیتورینگ

قابل مشاهده است.

---

#  سرویس‌های پروژه

| سرویس         | وظیفه                        |
| ------------- | ---------------------------- |
| Django        | ساخت API و مدیریت درخواست‌ها |
| Nginx         | Reverse Proxy                |
| Gunicorn      | اجرای Django Worker          |
| PostgreSQL    | Database اصلی                |
| Redis         | Message Broker               |
| Celery Worker | اجرای Taskهای Async          |
| Celery Beat   | اجرای Taskهای زمان‌بندی شده  |
| smtp4dev      | تست ایمیل                    |
| Flower        | مانیتورینگ Celery            |
| Locust        | تست فشار API                 |

---

#  اجرای پروژه

ابتدا فایل تنظیمات محیطی را بسازید:

```bash
cp .env.example .env
```

سپس:

```bash
docker compose up --build
```

بررسی وضعیت:

```bash
docker compose ps
```

باید تمام سرویس‌ها Running باشند.

---

#  آدرس سرویس‌ها

| سرویس      | آدرس                                                           |
| ---------- | -------------------------------------------------------------- |
| Django API | [http://localhost](http://localhost)                           |
| smtp4dev   | [http://localhost:5000](http://localhost:5000)                 |
| Flower     | [http://localhost:5555/flower/](http://localhost:5555/flower/) |
| Locust     | [http://localhost:8089](http://localhost:8089)                 |

---

#  تست دستی سیستم

ثبت کاربر:

```bash
curl -X POST http://localhost/api/register/ \
-H "Content-Type: application/json" \
-d '
{
"username":"Bahram",
"email":"devops523@gmail.comm",
"password":"12345678"
}
'
```

پاسخ شامل Task ID خواهد بود.

مثال:

```json
{
"user":"ali",
"task_id":"xxxxxxxx"
}
```

---

بررسی وضعیت Task:

```bash
curl http://localhost/api/tasks/<task_id>/
```

نتیجه:

قبل از اجرا:

```
PENDING
```

بعد از موفقیت:

```
SUCCESS
```

---

#  مشاهده ایمیل

وارد شوید:

```
http://localhost:5000
```

ایمیل Welcome را مشاهده خواهید کرد.

---

#  مشاهده Taskها با Flower

آدرس:

```
http://localhost:5555/flower/
```

در Flower می‌توانید ببینید:

* Workerها
* Taskهای اجرا شده
* Taskهای موفق
* Taskهای شکست خورده
* Queue ها

---

#  Celery Beat

این پروژه یک Task زمان‌بندی شده دارد:

```
cleanup_old_task_results
```

که هر 60 ثانیه اجرا می‌شود.

مشاهده Log:

```bash
docker compose logs -f celery-beat celery-worker
```

---

#  Load Testing با Locust

ورود:

```
http://localhost:8089
```

تنظیم کنید:

```
Users:
100

Spawn Rate:
10
```

Locust درخواست‌های ثبت‌نام را ارسال می‌کند و کل مسیر زیر را تست می‌کند:

```
Request

 ↓

Django

 ↓

PostgreSQL

 ↓

Redis

 ↓

Celery

 ↓

Email
```

---

#  ساختار پروژه

```
celery-drf-demo/

├── src/

│   ├── manage.py

│   ├── config/

│   │   ├── settings.py

│   │   ├── celery.py

│   │   ├── urls.py

│   │   └── wsgi.py


│   └── notifications/

│       ├── tasks.py
│       ├── views.py
│       ├── serializers.py
│       └── urls.py


├── docker/

│   ├── django/

│   └── nginx/


├── docker-compose.yml

├── requirements.txt

├── locustfile.py

└── .env.example

```

---

#  مفاهیم آموزشی این پروژه

با مطالعه این پروژه مفاهیم زیر را یاد می‌گیرید:

### Django

* Django REST Framework
* API Design
* Database Integration

### Celery

* Async Task
* Worker
* Broker
* Result Backend
* Beat Scheduler

### Redis

* Message Queue
* Task Distribution

### Production Deployment

* Nginx Reverse Proxy
* Gunicorn
* Docker Compose

### Monitoring

* Flower
* Task Tracking

### Testing

* Locust Load Testing
* Automated Tests

---

# نکات Production

این پروژه آموزشی است.

برای Production واقعی باید موارد زیر اضافه شوند:

* HTTPS با SSL
* Secrets Management
* Authentication واقعی
* Rate Limiting
* Prometheus + Grafana
* Logging مرکزی
* Kubernetes Deployment

---

#  Author
Jamall(Bahram) Mahmoudi

devops523@gmail.com

Created for learning and demonstrating:

**Django + Celery + Redis + Docker Production Architecture**

---

# ⭐ اگر این پروژه برای شما مفید بود

یک Star در GitHub بزنید ⭐

