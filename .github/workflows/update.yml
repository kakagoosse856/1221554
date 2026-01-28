name: OMNIX Auto Update

on:
  schedule:
    - cron: "0 */6 * * *"   # كل 6 ساعات
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: pip install -r requirements.txt

      - name: Run scraper
        run: python omnix_v5on_real.py

      - name: Commit & Push
        run: |
          git config user.name "omnix-bot"
          git config user.email "bot@omnix"
          git add playlist/*.m3u
          git commit -m "Auto update playlist" || echo "No changes"
          git push
