"""
🏆 自动化报名脚本
帮 master 自动完成 Qwen Global AI Hackathon 报名流程

用法:
  python3 auto_register.py

功能:
  1. 获取 Qwen API Key（阿里云百炼平台）
  2. 注册 Devpost 比赛

注意:
  - 需要手动完成登录/验证码
  - API Key 只会保存在本地 .env 文件中
  - 不会上传任何信息到第三方
"""

import os
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent

# ══════════════ 检查 Playwright ══════════════
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ 需要安装 playwright")
    print("   pip3 install playwright && python3 -m playwright install chromium")
    sys.exit(1)


def print_step(n: int, title: str):
    """打印步骤"""
    print(f"\n{'='*60}")
    print(f"  Step {n}: {title}")
    print(f"{'='*60}")


def wait_for_user_login(page, url: str, service_name: str):
    """
    打开页面让用户手动登录
    返回登录成功后的 page
    """
    print(f"\n🔗 打开 {service_name} 登录页...")
    page.goto(url, wait_until="domcontentloaded")
    print(f"📱 请在浏览器中完成 {service_name} 的登录")
    print("   （如果需要验证码，请手动输入）")
    print(f"   登录成功后，按 Enter 继续...")
    input()
    return page


# ══════════════ Step 1: 获取 Qwen API Key ══════════════
def get_qwen_api_key():
    """
    自动导航到阿里云百炼 API Key 页面
    用户手动登录后，协助创建 API Key
    """
    print_step(1, "获取 Qwen API Key（阿里云百炼）")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
        )
        page = context.new_page()

        # 打开阿里云百炼控制台
        print("\n📋 阿里云百炼 API Key 管理页")
        print("   如果没有阿里云账号，请先注册：https://www.aliyun.com")
        page.goto(
            "https://bailian.console.aliyun.com/?tab=model#/api-key",
            wait_until="domcontentloaded",
        )

        print("\n📱 请在浏览器中完成以下操作：")
        print("   1. 登录阿里云账号")
        print("   2. 如果是第一次使用，点击「开通百炼」")
        print("   3. 进入 API Key 管理页面后")
        print("   4. 点击「创建 API Key」")
        print("   5. 复制生成的 API Key（sk-xxx）")
        print()
        api_key = input("📋 请粘贴你复制的 API Key 到这里: ").strip()

        browser.close()

        if api_key.startswith("sk-"):
            # 保存到 .env
            env_path = PROJECT_DIR / ".env"
            env_content = f"QWEN_API_KEY={api_key}\n"

            # 如果已有 .env，追加或更新
            if env_path.exists():
                existing = env_path.read_text()
                lines = existing.strip().split("\n")
                new_lines = []
                replaced = False
                for line in lines:
                    if line.startswith("QWEN_API_KEY="):
                        new_lines.append(f"QWEN_API_KEY={api_key}")
                        replaced = True
                    else:
                        new_lines.append(line)
                if not replaced:
                    new_lines.append(f"QWEN_API_KEY={api_key}")
                env_content = "\n".join(new_lines) + "\n"

            env_path.write_text(env_content)
            print(f"✅ API Key 已保存到 {env_path}")
            return api_key
        else:
            print("⚠️ API Key 格式看起来不对（应该以 sk- 开头）")
            print(f"   你输入的是: {api_key}")
            confirm = input("   确定保存吗？(y/n): ").strip().lower()
            if confirm == "y":
                env_path = PROJECT_DIR / ".env"
                env_path.write_text(f"QWEN_API_KEY={api_key}\n")
                print(f"✅ 已保存")
                return api_key
            return None


# ══════════════ Step 2: Devpost 注册 ══════════════
def register_devpost():
    """
    打开 Devpost 比赛页面
    用户手动注册/登录后，自动点击 Register
    """
    print_step(2, "注册 Devpost 比赛")

    print("\n💡 Devpost 是国际最大的黑客松平台")
    print("   比赛链接（二选一）：")
    print("   A) 直接搜: devpost.com → 搜 'Qwen Cloud Global AI Hackathon'")
    print("   B) 试试: https://qwen-cloud-global-ai-hackathon.devpost.com")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
        )
        page = context.new_page()

        # 先尝试直接打开比赛页面
        hackathon_url = "https://devpost.com"
        print(f"\n🔗 打开 Devpost: {hackathon_url}")
        page.goto(hackathon_url, wait_until="domcontentloaded")

        print("\n📱 请在浏览器中完成以下操作：")
        print("   1. 右上角 Sign Up / Log In 注册账号")
        print("      （推荐用 GitHub 一键登录）")
        print("   2. 搜索 'Global AI Hackathon with Qwen Cloud'")
        print("   3. 进入比赛页面")
        print("   4. 点击 'Register for this hackathon'")
        print()
        input("   完成后按 Enter 继续...")

        current_url = page.url
        print(f"   当前页面: {current_url}")

        # 尝试找 Register 按钮
        try:
            register_btn = page.locator(
                'a:has-text("Register"), button:has-text("Register")'
            ).first
            if register_btn.is_visible(timeout=3000):
                print("   🎯 找到 Register 按钮，自动点击...")
                register_btn.click()
                time.sleep(2)
                print("   ✅ 已点击 Register")
        except:
            pass

        # 检查是否需要选择赛道
        try:
            track_select = page.locator('select, input[type="checkbox"]').first
            if track_select.is_visible(timeout=2000):
                print("   📋 可能需要选择赛道，请手动选择 Track 4: Autopilot Agent")
        except:
            pass

        print(f"\n   当前页面: {page.url}")
        print("   请确认报名状态...")
        input("   按 Enter 结束...")

        browser.close()


# ══════════════ Step 3: 验证配置 ══════════════
def verify_setup():
    """验证所有配置是否正确"""
    print_step(3, "验证配置")

    env_path = PROJECT_DIR / ".env"

    if env_path.exists():
        content = env_path.read_text()
        if "QWEN_API_KEY" in content:
            print("✅ QWEN_API_KEY 已配置")
        else:
            print("⚠️ .env 文件中未找到 QWEN_API_KEY")
    else:
        print("⚠️ .env 文件不存在")

    # 检查是否能导入 app
    print("\n📦 检查依赖...")
    deps_ok = True
    for dep in ["streamlit", "openai", "PyPDF2", "dotenv"]:
        try:
            __import__(dep.replace("-", "_"))
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} 未安装")
            deps_ok = False

    if not deps_ok:
        print("\n💡 运行以下命令安装缺失依赖:")
        print("   pip3 install -r requirements.txt")

    print("\n" + "=" * 60)
    print("  🎉 配置检查完成！")
    print("  ")
    print("  启动项目: cd ai-hackathon-starter && streamlit run app.py")
    print("  打开浏览器: http://localhost:8501")
    print("=" * 60)


# ══════════════ 主菜单 ══════════════
def main():
    print("""
╔══════════════════════════════════════════════╗
║  🏆 DocGuard · 比赛报名自动化             ║
║  Qwen Global AI Hackathon 2026            ║
║  Track 4: Autopilot Agent                ║
╚══════════════════════════════════════════════╝

小可帮你自动完成以下步骤：
  1️⃣  获取 Qwen API Key（阿里云百炼 · 免费）
  2️⃣  注册 Devpost 比赛
  3️⃣  验证所有配置

⚠️  提示：
  - 需要手动登录网站（小可不能替你输入密码）
  - 验证码需要手动完成
  - 所有信息只保存在本地，不会上传
""")

    input("按 Enter 开始...")

    # Step 1: API Key
    api_key = get_qwen_api_key()

    # Step 2: Devpost
    if api_key:
        do_devpost = input("\n📋 要打开 Devpost 报名吗？(y/n): ").strip().lower()
        if do_devpost == "y":
            register_devpost()
    else:
        print("\n⚠️ 跳过 Devpost 注册（需要先有 API Key）")
        print("   你可以之后手动注册: https://devpost.com")

    # Step 3: 验证
    verify_setup()

    print("\n🎯 下一步：")
    print("   cd ai-hackathon-starter")
    print("   streamlit run app.py")
    print("   然后上传一个 PDF 测试效果！")


if __name__ == "__main__":
    main()
