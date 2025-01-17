from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from textwrap import wrap
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class Link(Flowable):
    """
    A custom flowable that creates a clickable hyperlink.
    """

    def __init__(self, text, url, style=None):
        Flowable.__init__(self)
        self.text = text
        self.url = url
        self.style = style

    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(self.style.textColor if self.style else colors.blue)
        self.canv.setFont(self.style.fontName if self.style else "Helvetica", self.style.fontSize if self.style else 12)
        self.canv.drawString(0, 0, self.text)
        self.canv.linkURL(self.url, (0, 0, self.canv.stringWidth(self.text), self.style.fontSize if self.style else 12), relative=1)
        self.canv.restoreState()

    def wrap(self, availWidth, availHeight):
        # The width is the width of the text
        width = self.canv.stringWidth(self.text, self.style.fontName if self.style else "Helvetica", self.style.fontSize if self.style else 12)
        height = self.style.fontSize if self.style else 12
        return width, height

def create_pdf(data, topic, filename):
    """
    Generates a visually appealing PDF report with clickable links from a list of research paper summaries.

    Args:
        data: A list of dictionaries, where each dictionary represents a research paper summary.
        filename: The name of the PDF file to be generated.
    """

    doc = SimpleDocTemplate(filename, pagesize=landscape(letter),
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    elements = []

    # --- Styles ---
    styles = getSampleStyleSheet()

    # Custom Heading Style
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),  # Dark Blue
        alignment=1,  # Center
        spaceAfter=24,
    )

    # Custom Heading Style
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#003366'),  # Dark Blue
        alignment=0,  # Left
        spaceAfter=12,
    )

    # Subheading Style
    subheader_style = ParagraphStyle(
        'SubheaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#336699'),  # Lighter Blue
        spaceAfter=6,
    )

    # Body Text Style
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.black,
        leading=14,
    )

    # Link Style
    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.blue,
        underline=True
    )

    # --- Title Page ---
    elements.append(Paragraph(f"<b>{topic.capitalize()}</b>", title_style))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("A Curated Selection of Cutting-Edge Research", subheader_style))
    elements.append(Spacer(1, 1 * inch))
    elements.append(PageBreak())

    # --- Content Pages ---
    for item in data:
        # Page Title/Header
        elements.append(Paragraph(item.get('title', 'N/A'), header_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Table for Content
        table_data = [
            [Paragraph("<b>Central Topic</b>", subheader_style), Paragraph(wrap_text(item.get('central_topic', 'N/A'), body_style), body_style)],
            [Paragraph("<b>Concise Summary</b>", subheader_style), Paragraph(wrap_text(item.get('concise_summary', 'N/A'), body_style), body_style)],
            [Paragraph("<b>Key Insights</b>", subheader_style), Paragraph(wrap_text(item.get('key_insights', 'N/A'), body_style), body_style)],
            [Paragraph("<b>Research Gaps</b>", subheader_style), Paragraph(wrap_text(item.get('research_gaps', 'N/A'), body_style), body_style)],
            [Paragraph("<b>Link</b>", subheader_style), Link(item.get('links', 'N/A'), item.get('links', '#'), link_style)] 
        ]

        # Table Style
        table = Table(table_data, colWidths=[1.5 * inch, 6 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
        ]))

        elements.append(table)
        elements.append(PageBreak())

    # --- Build the PDF ---
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

def wrap_text(text, style):
    """Wraps text for better readability in table cells."""
    wrapped_lines = []
    for line in text.split('\n'):
        wrapped_lines.extend(wrap(line, width=85))  # Adjust width as needed
    return "<br/>".join(wrapped_lines)

def add_footer(canvas, doc):
    """Adds a footer to each page."""
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    footer_text = "ResearchGen AI: Your Gateway to Smarter, Faster Research"
    canvas.drawString(inch, 0.5 * inch, footer_text)
    canvas.drawRightString(doc.pagesize[0] - inch, 0.5 * inch, "Page %d" % doc.page)
    