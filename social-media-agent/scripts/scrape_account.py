#!/usr/bin/env python3
"""
scrape_account.py — 抓取单个 Instagram 账号的公开数据

用法:
  python3 scrape_account.py <handle> [post_count]

示例:
  python3 scrape_account.py bubbleula 9
  python3 scrape_account.py @bubbleula 9

输出: JSON 格式，包含账号基础数据 + 最近 N 条帖子的互动数据
"""

import subprocess
import json
import re
import time
import sys

def run_agent(cmd):
    """通过 agent-browser 执行 JS 并返回结果"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()

def extract_numbers(text):
    """从文本中提取数字（用于粉丝/帖子数）"""
    nums = re.findall(r'[\d,]+', text)
    return [n.replace(',', '') for n in nums]

def scrape_account(handle: str, post_count: int = 9) -> dict:
    """抓取单个 Instagram 账号"""
    # 清理 handle
    handle = handle.lstrip('@').rstrip('/')
    url = f"https://www.instagram.com/{handle}/"

    result = {
        "handle": handle,
        "url": url,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "account": {},
        "posts": [],
        "related_accounts": [],
        "errors": []
    }

    # Step 1: 打开主页
    print(f"  → Opening https://www.instagram.com/{handle}/")
    out = run_agent(f'agent-browser open https://www.instagram.com/{handle}/')
    time.sleep(7)

    # Step 2: 提取账号基本信息
    print(f"  → Extracting account data...")
    script = r"""
(function() {
  var body = document.body.innerText;
  var lines = body.split('\n').map(function(l){return l.trim();}).filter(function(l){return l.length > 0;});
  var r = {username: '', followers: 0, posts: 0, following: 0, bio: '', bioSnippet: '', category: '', location: '', isPrivate: false, latestPostUrls: []};

  // Parse lines for metrics
  for (var i = 0; i < lines.length; i++) {
    var l = lines[i];
    if (l.match(/^[\d,]+\s+posts$/)) r.posts = parseInt(l.replace(/[^\d]/g,''));
    if (l.match(/^[\d,]+\s+followers$/)) r.followers = parseInt(l.replace(/[^\d]/g,''));
    if (l.match(/^[\d,]+\s+following$/)) r.following = parseInt(l.replace(/[^\d]/g,''));
    if (l.match(/^[\d,]+\s+followers$/i)) r.username = lines[Math.max(0,i-1)];
  }

  // Bio: after following
  var pidx = body.indexOf('following');
  if (pidx > 0) {
    var after = body.substring(pidx, pidx + 600);
    var lines2 = after.split('\n').map(function(l){return l.trim();}).filter(function(l){return l.length > 0;});
    r.bioSnippet = lines2.slice(1, 8).join(' | ');
  }

  // Category
  var cat = document.querySelector('header span a, header span');
  if (cat) r.category = cat.innerText || '';

  // Location
  var loc = document.querySelector('a[href*="/explore/locations/"]');
  if (loc) r.location = loc.innerText || '';

  // Private check
  var loginBtn = document.querySelector('button[textContent*="Log in"], a[href*="login"]');
  r.isPrivate = !!loginBtn;

  // Latest post URLs
  var links = document.querySelectorAll('a[href]');
  var posts = [];
  links.forEach(function(l) {
    var h = l.href;
    if ((h.match(/\/p\/[a-zA-Z0-9_-]+/) || h.match(/\/reel\/[a-zA-Z0-9_-]+/)) && h.includes('/' + (r.username || '%s') + '/')) {
      posts.push(h);
    }
  });
  r.latestPostUrls = [...new Set(posts)].slice(0, %d);
  r.username = r.username || '%s';

  return JSON.stringify(r);
})()
""" % (post_count, handle)

    try:
        out = run_agent(f"agent-browser eval --stdin '{script}'")
        data = json.loads(out) if out.startswith('{') else {}
        result["account"] = data
        result["account"]["username"] = data.get("username", handle)
        print(f"    ✓ Followers: {data.get('followers','N/A')} | Posts: {data.get('posts','N/A')}")
        print(f"    ✓ Bio: {data.get('bioSnippet','')[:80]}")

        # Step 3: 抓取每条帖子
        post_urls = data.get("latestPostUrls", [])
        if not post_urls:
            print(f"    ⚠ No post URLs found (may be private or not loaded)")
            result["errors"].append("No post URLs found - account may be private or page didn't load")

        for i, post_url in enumerate(post_urls[:post_count]):
            print(f"  → Scraping post {i+1}/{min(len(post_urls),post_count)}: {post_url[-30:]}")
            time.sleep(2)
            try:
                run_agent(f'agent-browser open "{post_url}"')
                time.sleep(5)
                post_script = r"""
(function() {
  var og = document.querySelector('meta[property="og:description"]');
  var ts = document.querySelector('time');
  var vid = document.querySelector('meta[property="og:video"]');
  var img = document.querySelector('meta[property="og:image"]');
  var body = document.body.innerText;
  // Extract caption from body text
  var lines = body.split('\n');
  var captionLines = [];
  var inCaption = false;
  for (var i = 0; i < lines.length; i++) {
    var l = lines[i].trim();
    if (l.match(/^\d+[dwhm]$/) || l.match(/^\d+\s+hours?\s+ago$/i)) { inCaption = true; continue; }
    if (inCaption && l.length > 10 && !l.match(/^(Like|Reply|View all|Log in|Sign up)/i)) {
      captionLines.push(l);
    }
    if (captionLines.length > 20) break;
  }
  return JSON.stringify({
    url: window.location.href,
    ogDesc: og ? og.content : '',
    postedAt: ts ? ts.getAttribute('datetime') || ts.innerText : '',
    isVideo: !!vid,
    thumbnailUrl: img ? img.content : '',
    captionText: captionLines.slice(0,8).join(' ').substring(0, 500)
  });
})()
"""
                post_out = run_agent(f"agent-browser eval --stdin '{post_script}'")
                post_data = json.loads(post_out) if post_out.startswith('{') else {}
                if post_data:
                    # Parse og:description
                    og = post_data.get("ogDesc", "")
                    likes = 0
                    comments = 0
                    match = re.search(r'([\d,.]+)\s*like', og, re.I)
                    if match: likes = int(match.group(1).replace(',',''))
                    match = re.search(r'([\d,.]+)\s*comment', og, re.I)
                    if match: comments = int(match.group(1).replace(',',''))
                    followers = data.get("followers", 0)
                    er = round((likes + comments) / followers * 100, 2) if followers > 0 else 0

                    result["posts"].append({
                        "url": post_data.get("url", post_url),
                        "postedAt": post_data.get("postedAt", ""),
                        "likes": likes,
                        "comments": comments,
                        "engagementRate": er,
                        "caption": post_data.get("captionText", ""),
                        "isVideo": post_data.get("isVideo", False),
                    })
                    print(f"    ✓ {likes} likes, {comments} comments | ER: {er}%")
            except Exception as e:
                result["errors"].append(f"Post {i+1} error: {str(e)}")
                print(f"    ✗ Error: {e}")

    except Exception as e:
        result["errors"].append(f"Account scrape error: {str(e)}")
        print(f"    ✗ Error: {e}")

    # 返回主页
    run_agent(f'agent-browser open https://www.instagram.com/{handle}/')
    time.sleep(3)

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 scrape_account.py <handle> [post_count]")
        print("示例: python3 scrape_account.py bubbleula 9")
        sys.exit(1)

    handle = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 9

    print(f"\n=== Scraping @{handle.lstrip('@')} ===")
    data = scrape_account(handle, count)
    print(f"\n=== Done ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
