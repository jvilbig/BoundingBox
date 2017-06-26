from flask import Flask, jsonify, redirect, render_template, request
import labelling_web_app.db.access as db
import labelling_web_app.storage.b2 as b2
import base64
import json
import urllib2

id_and_key = 'hexAccountId_value:accountKey_value'
basic_auth_string = 'Basic ' + base64.b64encode(id_and_key)
headers = { 'Authorization': basic_auth_string }

request = urllib2.Request(
    'https://api.backblazeb2.com/b2api/v1/b2_authorize_account',
    headers = headers
    )
response = urllib2.urlopen(request)
response_data = json.loads(response.read())
response.close()

print 'auth token:', response_data['authorizationToken']
print 'api url:', response_data['apiUrl']
print 'download url:', response_data['downloadUrl']
print 'minimum part size:', response_data['minimumPartSize']

app = Flask(__name__)


@app.route('/label')
def label_page():
    image_id = db.get_one_pending()
    if not image_id:
        return redirect('static/no_more_images.html')
    image_link = b2.get_download_url(image_id)
    return render_template('label.html', image_link=image_link, image_id=image_id)


@app.route('/post_label', methods=['POST'])
def label_post():
    payload = request.get_json()
    db.set_label(payload['image_id'], payload['labels'])
    return jsonify(status='OK')
