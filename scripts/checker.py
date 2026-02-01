name: M3U Playlist Auto-Checker

on:
  schedule:
    # تشغيل كل 3 ساعات
    - cron: '0 */3 * * *'
  
  # تشغيل يدوي
  workflow_dispatch:
    inputs:
      custom_urls:
        description: 'Custom M3U URLs (comma separated)'
        required: false
        default: ''
  
  # تشغيل عند التعديل
  push:
    paths:
      - '.github/workflows/check-m3u.yml'
      - 'scripts/checker.py'
      - 'playlists.json'

permissions:
  contents: write

jobs:
  check-playlists:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: 🐍 Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: 📦 Install dependencies
      run: |
        pip install requests
    
    - name: 🔍 Run M3U Checker
      id: checker
      run: |
        echo "Starting M3U playlist check..."
        python scripts/checker.py
    
    - name: 📊 Generate Summary
      if: always()
      id: summary
      run: |
        # إنشاء ملف summary
        echo "## M3U Playlist Check Summary" > summary.md
        echo "" >> summary.md
        
        if [ -f "check_results.json" ]; then
          # استخدام Python لإنشاء التقرير
          python3 -c "
import json, datetime

try:
    with open('check_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # تنسيق الوقت
    ts = data['timestamp']
    try:
        dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        time_str = ts
    
    print(f'**Check Time:** {time_str}')
    print(f'**Status:** {\"✅ Success\" if data[\"success\"] else \"❌ Failed\"}')
    print(f'**Valid Playlists:** {data[\"summary\"][\"valid_urls\"]}/{data[\"summary\"][\"total_urls_checked\"]}')
    if 'total_channels' in data['summary']:
        print(f'**Total Channels:** {data[\"summary\"][\"total_channels\"]}')
    print('')
    print('### Playlist Details:')
    print('| Status | URL | Channels |')
    print('|--------|-----|----------|')
    
    for item in data['details']:
        url_short = item['url']
        if len(url_short) > 50:
            url_short = url_short[:47] + '...'
        
        if item['status'] == 'valid':
            status_icon = '✅'
            channels = item.get('channels_count', 'N/A')
        else:
            status_icon = '❌'
            channels = '0'
        
        print(f'| {status_icon} | \`{url_short}\` | {channels} |')
        
except Exception as e:
    print(f'❌ Error generating summary: {str(e)}')
" >> summary.md
        else:
          echo "❌ No results file generated" >> summary.md
        
        echo "" >> summary.md
        echo "### 📁 Generated Files:" >> summary.md
        echo "- **\`merged_channels.m3u\`**: Combined playlist" >> summary.md
        echo "- **\`check_results.json\`**: Detailed results" >> summary.md
        
        # نسخ إلى GITHUB_STEP_SUMMARY
        cat summary.md >> $GITHUB_STEP_SUMMARY
    
    - name: 💾 Upload Artifacts
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: m3u-results
        path: |
          merged_channels.m3u
          check_results.json
          summary.md
        retention-days: 7
    
    - name: 📤 Auto Commit
      if: success()
      run: |
        # تكوين Git
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        
        # التحقق من التغييرات
        git add merged_channels.m3u check_results.json || echo "No files to add"
        
        # إذا كان هناك تغييرات، قم بالـ commit
        if ! git diff --cached --quiet; then
          echo "Changes detected, committing..."
          
          # الحصول على الإحصائيات
          if [ -f "check_results.json" ]; then
            STATS=$(python3 -c "
import json
try:
    with open('check_results.json') as f:
        data = json.load(f)
    valid = data['summary']['valid_urls']
    total = data['summary']['total_urls_checked']
    channels = data['summary'].get('total_channels', '?')
    print(f'{valid}/{total} playlists, {channels} channels')
except:
    print('Updated playlist')
")
          else
            STATS="Updated playlist"
          fi
          
          TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M")
          COMMIT_MSG="📡 Update M3U playlist ($STATS) - $TIMESTAMP"
          
          git commit -m "$COMMIT_MSG"
          git push
          echo "✅ Changes committed and pushed"
        else
          echo "📭 No changes to commit"
        fi
