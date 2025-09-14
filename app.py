from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os
import csv
from Tools import uploader
from Tools.image_overlay import generate_certificate, convert_png_to_pdf
from flask import send_from_directory
import threading
import json

# Load .env variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "dev-secret"


@app.route('/')
def index():
    return render_template('index.html', title="Home", user={"username": "John"})


@app.route('/generate', methods=['POST'])
def generate():
    """Generate certificate for user id posted from the form and upload to ImgBB."""
    user_id = request.form.get('id') or request.form.get('user_id')
    # print('USER_ID:', user_id)
    if not user_id:
        flash('Missing ID', 'error')
        return redirect(url_for('index'))

    csv_path = os.path.join('data', 'user_data', 'user.csv')
    user = None
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row.get('id')) == str(user_id):
                    user = row
                    break
    except FileNotFoundError:
        flash('User database not found', 'error')
        return redirect(url_for('index'))
    
    # print('USER_DATA:', user)

    if not user:
        flash(f'User with id {user_id} not found', 'error')
        return redirect(url_for('index'))

    # Paths (keep current folder structure)
    templates_dir = os.path.join('data', 'certificate')
    # pick first image file from templates_dir
    template_img = None
    if os.path.isdir(templates_dir):
        for fname in os.listdir(templates_dir):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                template_img = os.path.join(templates_dir, fname)
                break

    if not template_img:
        flash('No certificate template found', 'error')
        return redirect(url_for('index'))

    out_dir = os.path.join('data', 'generated')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"certificate_{user_id}.png")
    # print('OUT_PATH:', out_path)

    signs_dir = os.path.join('data', 'signs')
    # print('SIGNS_DIR:', signs_dir)

    try:
        generated_path = generate_certificate(template_img, out_path, user, signs_dir=signs_dir)
    except Exception as e:
        flash(f'Failed to generate certificate: {e}', 'error')
        return redirect(url_for('index'))

    # convert to PDF
    pdf_path = os.path.join(out_dir, f"certificate_{user_id}.pdf")
    try:
        convert_png_to_pdf(generated_path, pdf_path)
    except Exception as e:
        flash(f'Failed to convert to PDF: {e}', 'error')
        return redirect(url_for('index'))

    # Local download endpoints
    pdf_download_url = url_for('download_pdf', filename=os.path.basename(pdf_path))

    # Start background thread to upload the PNG to ImgBB so the UI isn't blocked.
    def _upload_and_record(png_path, fname):
        try:
            url = uploader.upload_img(png_path)
            # write result into a small JSON file for later retrieval
            os.makedirs(os.path.dirname(png_path), exist_ok=True)
            results_file = os.path.join('data', 'generated', 'upload_results.json')
            try:
                existing = {}
                if os.path.isfile(results_file):
                    with open(results_file, 'r', encoding='utf-8') as rf:
                        existing = json.load(rf)
                existing[fname] = {'url': url}
                with open(results_file, 'w', encoding='utf-8') as wf:
                    json.dump(existing, wf)
            except Exception:
                # ignore JSON write errors
                pass
        except Exception as e:
            # store error message
            results_file = os.path.join('data', 'generated', 'upload_results.json')
            try:
                existing = {}
                if os.path.isfile(results_file):
                    with open(results_file, 'r', encoding='utf-8') as rf:
                        existing = json.load(rf)
                existing[fname] = {'error': str(e)}
                with open(results_file, 'w', encoding='utf-8') as wf:
                    json.dump(existing, wf)
            except Exception:
                pass

    upload_thread = threading.Thread(target=_upload_and_record, args=(generated_path, os.path.basename(generated_path)), daemon=True)
    upload_thread.start()

    # Render a simple page with result (upload continues in background)
    return render_template('index.html', title='Result', user={'username': 'John'}, result_url='', pdf_download=pdf_download_url, image_name=os.path.basename(generated_path))



@app.route('/upload_status/<path:filename>')
def upload_status(filename):
    """Return upload status for a generated image.

    Response JSON: { 'status': 'pending'|'done'|'error', 'url': '<imgbb url>'?, 'error': '<error message>'? }
    """
    results_file = os.path.join('data', 'generated', 'upload_results.json')
    if not os.path.isfile(results_file):
        return {'status': 'pending'}
    try:
        with open(results_file, 'r', encoding='utf-8') as rf:
            data = json.load(rf)
        entry = data.get(filename)
        if not entry:
            return {'status': 'pending'}
        if 'url' in entry:
            return {'status': 'done', 'url': entry['url']}
        if 'error' in entry:
            return {'status': 'error', 'error': entry['error']}
    except Exception:
        return {'status': 'pending'}
    return {'status': 'pending'}



@app.route('/download/<path:filename>')
def download_image(filename):
    # Serve generated images from data/generated
    return send_from_directory(os.path.join('data', 'generated'), filename, as_attachment=True)


@app.route('/download_pdf/<path:filename>')
def download_pdf(filename):
    return send_from_directory(os.path.join('data', 'generated'), filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development")
