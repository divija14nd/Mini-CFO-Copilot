import io
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportlabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

def _figure_to_image_buffer(figure):
    """Converts a matplotlib figure to an in-memory image buffer."""
    if not figure:
        return None, None, None
    buf = io.BytesIO()
    figure.savefig(buf, format='PNG', dpi=300, bbox_inches='tight')
    buf.seek(0)
    # Get dimensions for aspect ratio calculation
    with Image.open(buf) as img:
        width, height = img.size
    buf.seek(0)
    return buf, width, height

def create_single_report_pdf(summary: str, figure) -> bytes:
    """Creates a PDF for a single question-answer report using reportlab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle', fontSize=16, leading=20,
                              alignment=1, spaceAfter=20))
    # Use a unique name for the custom style to avoid conflicts
    styles.add(ParagraphStyle(name='SingleReportBody', fontSize=10, leading=14,
                              spaceAfter=10))

    story = []
    
    # Title
    story.append(Paragraph("CFO Copilot Report", styles['ReportTitle']))

    # Summary Text (replace newlines with <br/> tags for reportlab)
    summary_html = summary.replace('\n', '<br/>')
    story.append(Paragraph(summary_html, styles['SingleReportBody']))
    
    # Chart Image
    img_buffer, img_width, img_height = _figure_to_image_buffer(figure)
    if img_buffer and img_width > 0:
        max_width = doc.width
        ratio = img_height / img_width
        story.append(ReportlabImage(img_buffer, width=max_width, height=max_width * ratio))
        
    doc.build(story)
    return buffer.getvalue()

def create_conversation_pdf(history: list) -> bytes:
    """Creates a PDF of the entire conversation history using reportlab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ConvTitle', fontSize=16, leading=20,
                              alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name='UserHeader', fontSize=10, leading=12,
                              textColor=HexColor('#166534'), fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='AssistantHeader', fontSize=10, leading=12,
                              textColor=HexColor('#1e3a8a'), fontName='Helvetica-Bold'))
    # Use a unique name for the custom style to avoid conflicts
    styles.add(ParagraphStyle(name='ConvBody', fontSize=10, leading=14,
                              spaceAfter=10, leftIndent=15))

    story = []
    story.append(Paragraph("CFO Copilot Conversation History", styles['ConvTitle']))

    for message in history:
        role = message["role"]
        content_html = message["content"].replace('\n', '<br/>')
        
        if role == "user":
            story.append(Paragraph("You:", styles['UserHeader']))
            story.append(Paragraph(content_html, styles['ConvBody']))
        
        elif role == "assistant":
            story.append(Paragraph("Copilot:", styles['AssistantHeader']))
            story.append(Paragraph(content_html, styles['ConvBody']))
            
            figure = message.get("figure")
            img_buffer, img_width, img_height = _figure_to_image_buffer(figure)
            if img_buffer and img_width > 0:
                max_width = doc.width - 15 # Adjust for indent
                ratio = img_height / img_width
                story.append(Spacer(1, 0.1*inch))
                story.append(ReportlabImage(img_buffer, width=max_width, height=max_width * ratio))
                story.append(Spacer(1, 0.2*inch))

    doc.build(story)
    return buffer.getvalue()

