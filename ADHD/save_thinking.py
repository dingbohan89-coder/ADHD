#!/usr/bin/env python3
import requests
import sys
from datetime import datetime

# API配置
HEADERS = {
    'apikey': 'sb_secret_RNvhWYkiwVM2JQPmxdJU6w_EgXwnC37',
    'Authorization': 'Bearer sb_secret_RNvhWYkiwVM2JQPmxdJU6w_EgXwnC37',
    'Content-Type': 'application/json'
}
USER_ID = 'aaaaaaaa-0000-0000-0000-000000000001'
SERVICE_PROCESS_ID = '77777777-0000-0000-0000-000000000001'

# 从命令行参数读取
if len(sys.argv) < 2:
    print("[ERROR] No operation specified")
    sys.exit(1)

operation = sys.argv[1]

# 参数检查
if operation == 'thinking' and len(sys.argv) < 9:
    print("[ERROR] Thinking needs 8 arguments")
    sys.exit(1)
elif operation == 'plan' and len(sys.argv) < 3:
    print("[ERROR] Plan needs 2 arguments")
    sys.exit(1)
elif operation == 'mood' and len(sys.argv) < 4:
    print("[ERROR] Mood needs 3+ arguments")
    sys.exit(1)

if operation == 'thinking':
    # 保存思考过程
    user_input = sys.argv[2]
    current_mood = sys.argv[3]
    keywords = sys.argv[4].split(',') if sys.argv[4] != 'null' else []
    intent_type = sys.argv[5]
    confidence = float(sys.argv[6])
    selected_agent = sys.argv[7]
    reasoning = sys.argv[8] if len(sys.argv) > 8 else ''

    url = 'https://awnzrspczmvwklnjhmcc.supabase.co/rest/v1/agent_thinking_process'
    data = {
        'user_input': user_input,
        'current_mood': current_mood,
        'detected_keywords': keywords,
        'intent_type': intent_type,
        'intent_confidence': confidence,
        'selected_agent': selected_agent,
        'reasoning': reasoning
    }

    try:
        r = requests.post(url, headers=HEADERS, json=data)
        if r.status_code == 201:
            print(f"[OK] Thinking saved: {r.status_code}")
        else:
            print(f"[ERROR] {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[ERROR] {e}")

elif operation == 'plan':
    # 智能保存日程计划：先查询今天是否已有记录
    plan_content = sys.argv[2]
    today = datetime.now().strftime('%Y-%m-%d')

    # 第1步：查询今天是否已有记录
    try:
        query_url = f'https://awnzrspczmvwklnjhmcc.supabase.co/rest/v1/daily_plans?user_id=eq.{USER_ID}&date=eq.{today}&select=id,plan_content'
        r = requests.get(query_url, headers=HEADERS)
        existing = r.json()

        if existing and len(existing) > 0:
            # 第2a步：已有记录，更新它
            existing_id = existing[0]['id']
            old_content = existing[0]['plan_content']
            new_content = f"{old_content}\n{plan_content}"  # 追加新计划

            update_url = f'https://awnzrspczmvwklnjhmcc.supabase.co/rest/v1/daily_plans?id=eq.{existing_id}'
            update_data = {'plan_content': new_content}

            r_update = requests.patch(update_url, headers=HEADERS, json=update_data)
            if r_update.status_code in [200, 204]:
                print(f"[OK] Plan updated: {r_update.status_code} (appended to existing)")
            else:
                print(f"[ERROR] Update failed: {r_update.status_code}: {r_update.text}")
        else:
            # 第2b步：没有记录，插入新记录
            url = 'https://awnzrspczmvwklnjhmcc.supabase.co/rest/v1/daily_plans'
            data = {
                'user_id': USER_ID,
                'service_process_id': SERVICE_PROCESS_ID,
                'date': today,
                'plan_content': plan_content,
                'status': 'active'
            }

            r_insert = requests.post(url, headers=HEADERS, json=data)
            if r_insert.status_code == 201:
                print(f"[OK] Plan saved: {r_insert.status_code} (new record)")
            else:
                print(f"[ERROR] Insert failed: {r_insert.status_code}: {r_insert.text}")

    except Exception as e:
        print(f"[ERROR] {e}")

elif operation == 'mood':
    # 保存氛围切换
    from_mood = sys.argv[2] if sys.argv[2] != 'null' else 'initial'
    to_mood = sys.argv[3]
    trigger = sys.argv[4] if len(sys.argv) > 4 else ''
    thinking_id = sys.argv[5] if len(sys.argv) > 5 else None

    url = 'https://awnzrspczmvwklnjhmcc.supabase.co/rest/v1/mood_switches'
    data = {
        'user_id': USER_ID,
        'from_mood': from_mood,
        'to_mood': to_mood,
        'trigger_reason': trigger,
        'thinking_process_id': thinking_id
    }

    try:
        r = requests.post(url, headers=HEADERS, json=data)
        if r.status_code == 201:
            print(f"[OK] Mood switch saved: {r.status_code}")
        else:
            print(f"[ERROR] {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[ERROR] {e}")
