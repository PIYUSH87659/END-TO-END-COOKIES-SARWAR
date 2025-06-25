from flask import Flask, request, jsonify, render_template
import requests
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        cookie = data.get('cookie')
        uid = data.get('uid')
        message = data.get('message')

        # ✅ HTTP headers with cookie
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Cookie': cookie
        }

        # ✅ Step 1: Get fb_dtsg and jazoest
        r = requests.get("https://m.facebook.com/messages", headers=headers)
        fb_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', r.text)
        jazoest = re.search(r'name="jazoest" value="(.*?)"', r.text)

        if not fb_dtsg or not jazoest:
            return jsonify(success=False, error="❌ fb_dtsg or jazoest not found. Invalid or expired cookie.")

        # ✅ Step 2: Prepare message payload
        payload = {
            'fb_dtsg': fb_dtsg.group(1),
            'jazoest': jazoest.group(1),
            'body': message,
            'tids': f'cid.c.{uid}',
            'source': 'source:chat:web',
            'offline_threading_id': '1234567890123456',
            'message_id': '1234567890123456',
            'client': 'mercury'
        }

        send = requests.post('https://www.facebook.com/messages/send/', data=payload, headers=headers)

        if send.status_code == 200:
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="❌ Failed to send message. Check UID or cookie.")
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)