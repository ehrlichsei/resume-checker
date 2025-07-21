from flask import Blueprint, request, jsonify, send_from_directory, g
from werkzeug.utils import secure_filename
from models import db, User, Resume
from pdf_processor import PDFProcessor
# from photo_analyzer import PhotoAnalyzer  # temparorily deactivated
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from tempfile import NamedTemporaryFile
import uuid
from auth_utils import create_token, login_required

# Optional: simple PDF generation via reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

resumes_bp = Blueprint('resumes', __name__, url_prefix='/api/resumes')

@resumes_bp.route('/upload', methods=['POST'])
def upload_resume():
    """Upload a resume PDF and create a record
    ---
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            properties:
              email:
                type: string
              resume:
                type: string
                format: binary
    responses:
      200:
        description: Upload successful
        content:
          application/json:
            schema:
              type: object
              properties:
                resume_slug:
                  type: string
    """
    if 'email' not in request.form or 'resume' not in request.files:
        return jsonify({'error': 'Missing email or resume file'}), 400

    email = request.form['email']
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        # Create or get user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()

        # Create resume record with random slug
        slug = uuid.uuid4().hex[:16]
        print("Generated slug:", slug)
        resume = Resume(user_id=user.id, filename=filename, slug=slug)
        db.session.add(resume)
        db.session.commit()

        # Create login token (magic link could also be emailed)
        token = create_token(user.id)
        return jsonify({
            'message': 'File uploaded successfully',
            'resume_slug': slug,
            'token': token
        })

    return jsonify({'error': 'Failed to upload file'}), 400

@resumes_bp.route('/<string:slug>', methods=['GET'])
@login_required
def get_resume(slug):
    resume = Resume.query.filter_by(slug=slug, user_id=g.user_id).first_or_404()
    return jsonify({
        'id': resume.id,
        'filename': resume.filename,
        'upload_date': resume.upload_date.isoformat(),
        'processed': resume.processed,
        'analysis': resume.analysis,
        'user_email': resume.user.email if resume.user else None
    })

@resumes_bp.route('/<string:slug>/analyze', methods=['POST'])
@login_required
def analyze_resume(slug):
    """Analyze the uploaded resume and return markdown
    ---
    parameters:
      - in: path
        name: slug
        required: true
        schema:
          type: string
    responses:
      200:
        description: Analysis markdown
        content:
          application/json:
            schema:
              type: object
              properties:
                analysis_markdown:
                  type: string
    """
    resume = Resume.query.filter_by(slug=slug, user_id=g.user_id).first_or_404()

    # Always (re)analyze on demand and return Markdown directly. We deliberately
    # avoid persisting the string to the `analysis` JSON column to bypass type
    # mismatch problems.

    filepath = os.path.join('uploads', resume.filename)
    pdf_processor = PDFProcessor()
    analysis_markdown = pdf_processor.analyze_resume(filepath)

    # Mark resume as processed so the UI can reflect the status, but do not
    # store the markdown string in the JSON field.
    if not resume.processed:
        resume.processed = True
        db.session.commit()

    return jsonify({
        'message': 'Analysis complete',
        'analysis_markdown': analysis_markdown
    })

# ------------ Send PDF via email -----------------

@resumes_bp.route('/<string:slug>/send-pdf', methods=['POST'])
@login_required
def send_pdf(slug):
    """Generate a simple PDF from the Markdown analysis and email it to the user."""
    resume = Resume.query.filter_by(slug=slug, user_id=g.user_id).first_or_404()

    # Re-run analysis to get latest markdown
    filepath = os.path.join('uploads', resume.filename)
    pdf_processor = PDFProcessor()
    analysis_md = pdf_processor.analyze_resume(filepath)

    if not REPORTLAB_AVAILABLE:
        return jsonify({'error': 'Server missing reportlab package for PDF generation'}), 500

    # Generate PDF with basic formatting using Platypus, which handles automatic wrapping
    tmp_pdf = NamedTemporaryFile(delete=False, suffix='.pdf')
    doc = SimpleDocTemplate(
        tmp_pdf.name,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()
    # --- Register a font that supports Chinese characters (e.g. NotoSansCJK) ---
    font_registered = False
    import glob
    possible_paths = [
        os.path.join(os.getcwd(), 'fonts', 'NotoSansCJKsc-Regular.otf'),
        os.path.join(os.getcwd(), 'fonts', 'NotoSansCJKsc-Regular.ttf'),
        os.path.join(os.getcwd(), 'NotoSansCJKsc-Regular.otf'),
        os.path.join(os.getcwd(), 'NotoSansCJKsc-Regular.ttf'),
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
    ]
    # also accept any NotoSans* TTF/OTF in ./fonts directory
    possible_paths.extend(glob.glob(os.path.join(os.getcwd(), 'fonts', 'NotoSans*.*tf')))
    for p in possible_paths:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont('NotoSans', p))
                font_registered = True
                break
            except Exception:
                pass
    else:
        font_registered = True

    # Fallback: if registration failed, Chinese will not render; continue with default

    # Ensure custom bullet style added only once to avoid KeyError on subsequent calls
    if "MarkdownBullet" not in styles.byName:
        styles.add(
            ParagraphStyle(
                name="MarkdownBullet",
                parent=styles["Normal"],
                bulletIndent=0,
                leftIndent=12,
                firstLineIndent=-6,
            )
        )

    # Override fonts if Chinese-capable font registered
    if font_registered:
        for name in ["Normal", "Heading2", "Heading3", "MarkdownBullet"]:
            if name in styles.byName:
                styles[name].fontName = 'NotoSans'

    story = []
    for raw in analysis_md.split("\n"):
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 10))
            continue

        # Simple markdown cues
        if line.startswith("###"):
            story.append(Paragraph(line[3:].strip(), styles["Heading3"]))
        elif line.startswith("##"):
            story.append(Paragraph(line[2:].strip(), styles["Heading2"]))
        elif line.startswith("- ") or line.startswith("• "):
            story.append(Paragraph(line[2:].strip(), styles["MarkdownBullet"]))
        else:
            story.append(Paragraph(line, styles["Normal"]))

    doc.build(story)

    # Prepare email
    msg = EmailMessage()
    msg['Subject'] = 'Your Resume Analysis Report'
    msg['From'] = 'hello@yulifangcoach.com'
    msg['To'] = resume.user.email if resume.user else None
    if not msg['To']:
        return jsonify({'error': 'User email not found'}), 400

    msg.set_content('Please find attached your resume analysis PDF generated on ' + datetime.utcnow().isoformat())

    with open(tmp_pdf.name, 'rb') as f:
        pdf_data = f.read()
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='analysis.pdf')

    # Send via SMTP (expects SMTP creds in env)
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

    return jsonify({'message': 'PDF emailed successfully'})

@resumes_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# ---------------- Profile picture extraction -----------------

@resumes_bp.route('/<string:slug>/profile-picture', methods=['GET'])
def get_profile_picture(slug):
    """Return the first image found in the uploaded PDF as the candidate's
    profile picture.  The image is extracted on demand and cached under
    `uploads/profile_pictures` for subsequent requests."""

    resume = Resume.query.filter_by(slug=slug).first_or_404()
    pdf_path = os.path.join('uploads', resume.filename)

    # Cache directory for extracted pictures
    pic_dir = os.path.join('uploads', 'profile_pictures')
    os.makedirs(pic_dir, exist_ok=True)

    # Build deterministic cache filename
    base_name, _ = os.path.splitext(resume.filename)
    cached_prefix = f"{base_name}_{resume.id}_profile."

    # Check if we have already extracted and stored a picture
    for file in os.listdir(pic_dir):
        if file.startswith(cached_prefix):
            return send_from_directory(pic_dir, file)

    # Extract the picture if not cached
    processor = PDFProcessor()
    try:
        img_bytes, ext = processor.extract_profile_picture(pdf_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    pic_filename = f"{cached_prefix}{ext}"
    pic_path = os.path.join(pic_dir, pic_filename)
    with open(pic_path, 'wb') as f:
        f.write(img_bytes)

    return send_from_directory(pic_dir, pic_filename)

# ---------------- Profile picture analysis -----------------

@resumes_bp.route('/<string:slug>/profile-picture/analysis', methods=['GET'])
def analyze_profile_picture(slug):
    """Return aesthetic and confidence metrics for the cached profile picture."""

    resume = Resume.query.filter_by(slug=slug).first_or_404()

    pic_dir = os.path.join('uploads', 'profile_pictures')
    base_name, _ = os.path.splitext(resume.filename)
    cached_prefix = f"{base_name}_{resume.id}_profile."

    # Locate cached image (must exist – ensure user hit extract endpoint first)
    pic_path = None
    for file in os.listdir(pic_dir):
        if file.startswith(cached_prefix):
            pic_path = os.path.join(pic_dir, file)
            break

    if not pic_path or not os.path.exists(pic_path):
        return jsonify({'error': 'Profile picture not found. Call /profile-picture first.'}), 404

    analyzer = PhotoAnalyzer()
    with open(pic_path, 'rb') as fp:
        result = analyzer.analyze(fp.read())

    return jsonify(result)
