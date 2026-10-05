import os
import time
import shutil
import subprocess
from playwright.sync_api import sync_playwright

def record():
    recordings_dir = os.path.abspath('docs/recordings')
    os.makedirs(recordings_dir, exist_ok=True)
    
    # Sync standalone HTML with updated JSON first
    with open('output/triaged_cases.json') as f:
        cases_json = f.read()
    with open('app/dashboard.html') as f:
        html = f.read()
    html_out = html.replace('let casesData = [];', f'let casesData = {cases_json};')
    html_out = html_out.replace('loadData();', 'renderTable();')
    with open('app/dashboard_standalone.html', 'w') as f:
        f.write(html_out)
    print('Refreshed dashboard_standalone.html with embedded evaluations.')

    chrome_bin = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome_bin,
            headless=True
        )
        context = browser.new_context(
            viewport={'width': 1600, 'height': 1000},
            record_video_dir=recordings_dir,
            record_video_size={'width': 1600, 'height': 1000}
        )
        page = context.new_page()
        
        # 1. Open Dashboard
        print("Navigating to dashboard...")
        page.goto('http://localhost:8088/app/dashboard_standalone.html')
        page.wait_for_selector('tbody#case-table-body tr')
        time.sleep(2)
        
        # 2. Scroll through KPI cards & case queue
        page.evaluate("window.scrollBy({ top: 350, behavior: 'smooth' })")
        time.sleep(2)
        page.evaluate("window.scrollBy({ top: -350, behavior: 'smooth' })")
        time.sleep(1.5)
        
        # Helper to search and open case
        def open_case(case_id):
            print(f"Searching and opening {case_id}...")
            page.fill('#search', case_id)
            time.sleep(1.2)
            row = page.locator(f"tbody#case-table-body tr:has-text('{case_id}')")
            row.wait_for(state='visible', timeout=5000)
            row.click()
            page.wait_for_selector('#modal-overlay.open', timeout=5000)
            time.sleep(2)

        def close_modal():
            print("Closing modal...")
            page.locator('.close-btn').click()
            time.sleep(1)
            page.fill('#search', '')
            time.sleep(1)

        # 3. Demonstrate Case PA-2609-8106: Adversarial Prompt Injection Fax
        print("--- DEMO 1: Adversarial Prompt Injection Neutralization ---")
        open_case('PA-2609-8106')
        time.sleep(2)
        page.evaluate("document.getElementById('modal-body').scrollBy({ top: 350, behavior: 'smooth' })")
        time.sleep(3)
        page.evaluate("document.getElementById('modal-body').scrollBy({ top: 500, behavior: 'smooth' })")
        time.sleep(3)
        close_modal()
        
        # 4. Demonstrate Case PA-2609-8100: Clean Lumbar MRI Approval & Copilot Checklist
        print("--- DEMO 2: Clean Approval & Agentic Checklist ---")
        open_case('PA-2609-8100')
        time.sleep(2)
        page.evaluate("document.getElementById('modal-body').scrollBy({ top: 450, behavior: 'smooth' })")
        time.sleep(3.5)
        page.evaluate("document.getElementById('modal-body').scrollBy({ top: 500, behavior: 'smooth' })")
        time.sleep(3.5)
        close_modal()
        
        # 5. Demonstrate Case PA-2609-8102: Arizona Riverbend MA (MD Licensing Mandate)
        print("--- DEMO 3: Riverbend MA in Arizona (Regulatory MD Mandate) ---")
        open_case('PA-2609-8102')
        time.sleep(2)
        page.evaluate("document.getElementById('modal-body').scrollBy({ top: 400, behavior: 'smooth' })")
        time.sleep(4)
        close_modal()
        
        # 6. Demonstrate Case PA-2609-8111: Harlan Freight Lines Plan Exclusion
        print("--- DEMO 4: Harlan Plan Exclusion & Deterministic Hierarchy ---")
        open_case('PA-2609-8111')
        time.sleep(2)
        page.evaluate("document.getElementById('modal-body').scrollBy({ top: 400, behavior: 'smooth' })")
        time.sleep(3.5)
        close_modal()
        
        # 7. Demonstrate Case PA-2609-8113: Incomplete Fax & Automated Deficiency Notice
        print("--- DEMO 5: Incomplete Fax & Instant Provider Deficiency Notice ---")
        open_case('PA-2609-8113')
        time.sleep(2)
        page.evaluate("document.getElementById('modal-body').scrollBy({ top: 400, behavior: 'smooth' })")
        time.sleep(4)
        close_modal()
        
        # 8. Filter by Status: Security Flagged, Incomplete, Ready
        print("--- DEMO 6: Queue Tab Filtering ---")
        page.locator("button:has-text('Security Flagged')").click()
        time.sleep(2.5)
        page.locator("button:has-text('Incomplete / Pended')").click()
        time.sleep(2.5)
        page.locator("button:has-text('Ready for Review')").click()
        time.sleep(2.5)
        page.locator("button:has-text('All Requests')").click()
        time.sleep(2.5)

        context.close()
        browser.close()
        print("Playwright recording completed successfully!")

    # Find the recorded webm file in recordings_dir
    files = [os.path.join(recordings_dir, f) for f in os.listdir(recordings_dir) if f.endswith('.webm')]
    if not files:
        raise RuntimeError("No video file generated by Playwright!")
    
    latest_webm = max(files, key=os.path.getctime)
    print("Recorded video file:", latest_webm)
    
    # Convert to MP4
    mp4_out = os.path.abspath('docs/bellcourt_demo_walkthrough.mp4')
    cmd_mp4 = [
        '/opt/homebrew/bin/ffmpeg', '-y',
        '-i', latest_webm,
        '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 'yuv420p',
        mp4_out
    ]
    subprocess.run(cmd_mp4, check=True)
    print("Compiled HD MP4:", mp4_out)

    # Convert to WebP
    webp_out = os.path.abspath('docs/bellcourt_demo_walkthrough.webp')
    cmd_webp = [
        '/opt/homebrew/bin/ffmpeg', '-y',
        '-i', latest_webm,
        '-vf', 'scale=1280:800',
        '-vcodec', 'libwebp', '-lossless', '0', '-compression_level', '4',
        '-q:v', '70', '-loop', '0',
        webp_out
    ]
    subprocess.run(cmd_webp, check=True)
    print("Compiled WebP animation:", webp_out)

    # Copy to artifacts directory
    artifact_dir = '/Users/vizzdd/.gemini/antigravity-ide/brain/7eaf1a7b-64e2-4c87-94a8-2c097077e76a'
    if os.path.exists(artifact_dir):
        shutil.copy(webp_out, os.path.join(artifact_dir, 'bellcourt_demo_walkthrough.webp'))
        print("Copied to conversation artifact directory!")

if __name__ == '__main__':
    record()
