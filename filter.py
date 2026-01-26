name: Filter Channels

on:
  workflow_dispatch:        # تشغيل يدوي
  schedule:
    - cron: "*/30 * * * *" # تشغيل تلقائي كل 30 دقيقة

jobs:
  filter:
    runs-on: ubuntu-latest

    steps:
      # 1️⃣ استنساخ المستودع
      - name: Checkout repository
        uses: actions/checkout@v3

      # 2️⃣ إعداد Python
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"

      # 3️⃣ تثبيت المكتبات المطلوبة
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install requests m3u8  # أضف أي مكتبات أخرى يحتاجها سكربتك

      # 4️⃣ تشغيل سكربت الفلترة
      - name: Run filter script
        run: python filter.py
        # إذا كان filter.py في مجلد فرعي استخدم:
        # run: python path/to/filter.py

      # 5️⃣ إضافة الملفات الناتجة ورفعها بأمان
      - name: Commit & push changes
        run: |
          git config user.name "BOT"
          git config user.email "bot@github.com"
          
          # إضافة أي ملفات m3u تم إنشاؤها
          git add *.m3u
          
          # إنشاء commit فقط إذا هناك تغييرات
          git diff-index --quiet HEAD || git commit -m "Update alive channels"
          
          # دفع التغييرات باستخدام HTTPS و GITHUB_TOKEN
          git push https://x-access-token:${GITHUB_TOKEN}@github.com/${{ github.repository }} HEAD:main
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
