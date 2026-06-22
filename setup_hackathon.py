"""
🏆 DocGuard 报名助手
直接打开浏览器到对应页面，master 手动操作即可

用法:
  python3 setup_hackathon.py qwen    # 打开阿里云百炼获取 API Key
  python3 setup_hackathon.py devpost # 打开 Devpost 报名
  python3 setup_hackathon.py all     # 全部打开
"""

import sys
import webbrowser
import time
from pathlib import Path

URLS = {
    "qwen": {
        "title": "🔑 获取 Qwen API Key（阿里云百炼）",
        "url": "https://bailian.console.aliyun.com/?tab=model#/api-key",
        "steps": [
            "1. 登录阿里云账号（没有就注册一个）",
            "2. 如果是第一次，点击「开通百炼」→ 免费额度自动到账",
            "3. 点击「创建 API Key」",
            "4. 复制生成的 Key（sk-xxx）",
            "5. 粘贴到下方 .env 文件中：",
            "",
            "   编辑: ai-hackathon-starter/.env",
            "   写入: QWEN_API_KEY=sk-你复制的key",
        ],
    },
    "devpost": {
        "title": "📝 注册 Devpost 比赛",
        "url": "https://devpost.com",
        "steps": [
            "1. 右上角 Sign Up（推荐 GitHub 登录）",
            "2. 搜索 'Global AI Hackathon with Qwen Cloud'",
            "3. 进入比赛页 → 点击 Register",
            "4. 选择 Track 4: Autopilot Agent",
            "5. 填写项目信息（可以先填个占位的，后面再改）",
        ],
    },
    "github": {
        "title": "🐙 创建 GitHub 仓库",
        "url": "https://github.com/new",
        "steps": [
            "1. Repository name: DocGuard",
            "2. Description: AI Autopilot for Document Review - Qwen Hackathon 2026",
            "3. Public（比赛要求开源）",
            "4. 不要勾选 Add README（我们已有）",
            "5. 创建后，终端执行以下命令推送代码：",
            "",
            "   cd ai-hackathon-starter",
            "   git init",
            "   git add .",
            '   git commit -m "🚀 DocGuard - Autopilot Agent for Qwen Hackathon"',
            "   git remote add origin https://github.com/你的用户名/DocGuard.git",
            "   git push -u origin main",
        ],
    },
    "qwen_register": {
        "title": "🎯 Qwen Cloud 黑客松专用额度申请",
        "url": "https://www.alibabacloud.com/campaign/qwen-hackathon-2026",
        "steps": [
            "1. 进入页面申请黑客松专用 API 额度",
            "2. 或者：直接开通 Model Studio 就有免费额度",
            "   https://www.alibabacloud.com/product/model-studio",
            "3. 国际站用户送 100万 Token 免费",
            "4. 中国站用户开通百炼送 7000万+ Token",
        ],
    },
}


def open_page(key: str):
    """打开页面并打印步骤"""
    info = URLS[key]
    print(f"\n{'='*60}")
    print(f"  {info['title']}")
    print(f"{'='*60}")
    print(f"\n📋 操作步骤：")
    for step in info["steps"]:
        print(f"   {step}")
    print(f"\n🔗 正在打开浏览器...")
    webbrowser.open(info["url"])
    print(f"   {info['url']}")
    print(f"\n✅ 浏览器已打开！按提示操作即可。")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 setup_hackathon.py qwen         # 获取 API Key")
        print("  python3 setup_hackathon.py devpost      # 注册 Devpost")
        print("  python3 setup_hackathon.py github       # 创建 GitHub 仓库")
        print("  python3 setup_hackathon.py all          # 全部打开")
        return

    cmd = sys.argv[1]

    if cmd == "all":
        for key in ["qwen", "devpost", "github"]:
            open_page(key)
            print()
            time.sleep(2)
    elif cmd in URLS:
        open_page(cmd)
    else:
        print(f"未知命令: {cmd}")
        print(f"可用: {list(URLS.keys())}")

    # 提示保存 API Key
    if cmd in ("qwen", "all"):
        env_path = Path(__file__).parent / ".env"
        print(f"\n{'='*60}")
        print(f"  💡 拿到 API Key 后的操作：")
        print(f"{'='*60}")
        print(f"   echo 'QWEN_API_KEY=sk-你的key' >> {env_path}")
        print(f"   或者直接编辑 {env_path} 文件")
        print(f"   然后就可以用 streamlit run app.py 测试啦！")


if __name__ == "__main__":
    main()
