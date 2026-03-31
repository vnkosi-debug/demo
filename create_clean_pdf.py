from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Create PDF
doc = SimpleDocTemplate("Agentic_Protocol_Clean.pdf", pagesize=letter,
                       rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    spaceAfter=30,
    alignment=1,  # Center
    textColor=colors.darkblue
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle',
    parent=styles['Heading2'],
    fontSize=18,
    spaceAfter=20,
    alignment=1,
    textColor=colors.darkred
)

section_style = ParagraphStyle(
    'Section',
    parent=styles['Heading3'],
    fontSize=14,
    spaceAfter=15,
    textColor=colors.darkgreen
)

normal_style = styles['Normal']
normal_style.fontSize = 11
normal_style.leading = 14

bullet_style = ParagraphStyle(
    'Bullet',
    parent=normal_style,
    leftIndent=20,
    bulletIndent=10
)

# Content
story = []

# Title
story.append(Paragraph("🚀 Agentic Protocol Engineering", title_style))
story.append(Paragraph("The Wiring Harness of Trust", subtitle_style))
story.append(Spacer(1, 0.3*inch))

# Problem Statement
story.append(Paragraph("🎯 The Production Reality Check", section_style))
story.append(Paragraph("Clean whiteboard diagrams hide dangerous gaps in agentic systems where trust leaks through the seams.", normal_style))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("❌ What Fails in Production:", normal_style))
story.append(Paragraph("• Timestamps vanish between retrieval and reasoning", bullet_style))
story.append(Paragraph("• Provenance gets stripped from critical data", bullet_style))
story.append(Paragraph("• Memory drifts without structured handoffs", bullet_style))
story.append(Paragraph("• Actions fire without governance checks", bullet_style))
story.append(Paragraph("• Tools execute with unchecked privileges", bullet_style))
story.append(Spacer(1, 0.2*inch))

# Solution
story.append(Paragraph("✅ The Protocol Solution: Trust That Travels", section_style))

# Table data
data = [
    ['Protocol', 'What It Does', 'Why It Matters'],
    ['🧩 MCP\nModel Context', 'Versioned, structured context slots', 'Models get predictable, validated inputs'],
    ['💬 ACP\nAgent Communication', 'Traceable message envelopes', 'Every conversation leaves an audit trail'],
    ['🤝 A2A\nAgent-to-Agent', 'Task coordination & state sync', 'Autonomous agents work together safely'],
    ['🌐 ANP\nAgent Network', 'Cross-org identity & policy', 'Trust extends beyond enterprise walls']
]

# Create table
table = Table(data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))

story.append(table)
story.append(Spacer(1, 0.2*inch))

# Maturity Ladder
story.append(Paragraph("📈 Maturity Ladder: From Fragile to Bulletproof", section_style))
story.append(Paragraph("🔴 L0: Ad Hoc Chaos → 🟠 L1: Sandbox Safety → 🟡 L2: Context Stability → 🟢 L3: Structured Communication → 🔵 L4: Federated Trust → 🟣 L5: Protocol Mesh", normal_style))
story.append(Spacer(1, 0.2*inch))

# Demo
story.append(Paragraph("🎪 Protocol Envelope Example", section_style))
demo_code = '''{
  "protocol": "ACP_Message",
  "metadata": {
    "id": "msg_1774875876",
    "session": "med_review_001",
    "timestamp": "2026-03-30T15:04:36Z"
  },
  "payload": {
    "tool": "generate_report",
    "execution_class": "restricted",
    "provenance": {
      "origin": "verified_medical_db",
      "trust_score": 0.95
    },
    "governance": {
      "requires_approval": true,
      "approver_role": "Chief_Medical_Officer"
    }
  }
}'''

code_style = ParagraphStyle(
    'Code',
    parent=normal_style,
    fontName='Courier',
    fontSize=9,
    backgroundColor=colors.lightgrey,
    borderColor=colors.grey,
    borderWidth=1,
    borderPadding=5,
    leftIndent=20
)

story.append(Paragraph(demo_code, code_style))
story.append(Spacer(1, 0.2*inch))

# Key Takeaway
story.append(Paragraph("💡 Key Takeaway", section_style))
story.append(Paragraph("APIs connect components. Protocols connect trust.", normal_style))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph('"The diagram is just a map. The protocols are the wiring harness that keeps the whole thing intact when it moves."', ParagraphStyle('Quote', parent=normal_style, leftIndent=40, rightIndent=40, fontSize=10)))
story.append(Paragraph("— Austin & Neter, Chapter 8", ParagraphStyle('Attribution', parent=normal_style, alignment=2, fontSize=9)))

# Build PDF
doc.build(story)
print("Clean PDF created: Agentic_Protocol_Clean.pdf")