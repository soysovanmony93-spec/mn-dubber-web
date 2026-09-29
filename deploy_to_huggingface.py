#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Deploy MN DUBBER PRO to Hugging Face Spaces (24/7 Free Cloud Hosting).
"""
import os
import sys

try:
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from huggingface_hub import HfApi

def main():
    print("\n" + "=" * 70)
    print("🚀 MN DUBBER PRO - AUTOMATIC DEPLOY TO HUGGING FACE SPACES (24/7 FREE)")
    print("=" * 70)
    print()
    
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        print("👉 ជំហានទី ១: យក Access Token (ឥតគិតថ្លៃ) ពី Link នេះ៖")
        print("   🔗 https://huggingface.co/settings/tokens")
        print("   (ចុច 'Create new token' -> ជ្រើសរើស Role: 'Write')")
        print()
        token = input("សូម Paste Hugging Face Token របស់អ្នកនៅទីនេះ: ").strip()
        
    if not token:
        print("\n[ERROR] Token មិនអាចទទេបានឡើយ! សូមព្យាយាមម្តងទៀត។")
        input("\nចុច Enter ដើម្បីចាកចេញ...")
        sys.exit(1)

    api = HfApi(token=token)
    try:
        user_info = api.whoami()
        username = user_info.get("name") or user_info.get("username")
        print(f"\n✅ បានភ្ជាប់ជោគជ័យជាមួយគណនី Hugging Face: @{username}")
    except Exception as e:
        print(f"\n[ERROR] Token មិនត្រឹមត្រូវ ឬផុតកំណត់: {e}")
        input("\nចុច Enter ដើម្បីចាកចេញ...")
        sys.exit(1)

    default_name = "mn-dubber-pro"
    print(f"\n👉 ជំហានទី ២: ដាក់ឈ្មោះ Space [ចុច Enter យក '{default_name}']")
    custom_name = input("ឈ្មោះ Space: ").strip()
    space_name = custom_name if custom_name else default_name
    space_name = space_name.lower().replace(" ", "-")
    repo_id = f"{username}/{space_name}"
    
    print(f"\n📦 [1/2] កំពុងបង្កើត Space: {repo_id} (Cloud 24/7 Docker)...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True
        )
        print("✅ Space ត្រូវបានរៀបចំរួចរាល់!")
    except Exception as e:
        print(f"ℹ️ {e}")

    source_folder = os.path.dirname(os.path.abspath(__file__))
    print(f"\n🚀 [2/2] កំពុង Upload ឯកសារកម្មវិធីទាំងអស់ទៅកាន់ Cloud Space...")
    print("   (ដំណើរការនេះចំណាយពេលប្រហែល 1-2 នាទី សូមរង់ចាំ)...")

    try:
        api.upload_folder(
            folder_path=source_folder,
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=[
                "uploads/*",
                "outputs/*",
                "scratch/*",
                "__pycache__/*",
                "*.pyc",
                "*.bat"
            ]
        )
        clean_subdomain = f"{username}-{space_name}".replace("_", "-").lower()
        public_url = f"https://{clean_subdomain}.hf.space"
        space_url = f"https://huggingface.co/spaces/{repo_id}"
        
        print("\n" + "=" * 70)
        print("🎉 អបអរសាទរ! កម្មវិធីត្រូវបាន Upload ទៅកាន់ Cloud 24/7 ជោគជ័យ!")
        print("=" * 70)
        print(f"👉 Link តាមដាន Build Status: {space_url}")
        print(f"📱 Link App លើទូរស័ព្ទ (24/7):   {public_url}")
        print()
        print("💡 Hugging Face នឹងចំណាយពេលប្រហែល 2-3 នាទីដើម្បី Build Docker Container ដំបូង។")
        print("   បន្ទាប់ពីនោះ Link ខាងលើនឹងដំណើរការ ២៤ម៉ោង/៧ថ្ងៃ (24/7) ជារៀងរហូត!")
        print("   កុំព្យូទ័ររបស់អ្នកបិទក៏ដោយ ក៏អ្នកដទៃនៅតែអាចបើកប្រើពីទូរស័ព្ទបាន ១០០%!")
        print("=" * 70 + "\n")
    except Exception as e:
        print(f"\n[ERROR] មានបញ្ហាក្នុងការ Upload: {e}")

    input("ចុច Enter ដើម្បីបញ្ចប់...")

if __name__ == "__main__":
    main()
