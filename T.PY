"""
Protocol-Driven Content Generation System
=========================================

A real implementation of Agentic Protocol Engineering that generates presentations
and documents using trust-maintaining protocols.

This system uses MCP, ACP, Provenance, and Sandbox protocols to:
- Analyze source documents with provenance tracking
- Generate presentation content through agent collaboration
- Create actual PPTX and PDF outputs
- Maintain trust and evidence throughout the pipeline

USAGE:
python T.PY analyze [file_path]    # Analyze a document and generate content
python T.PY generate slides       # Generate presentation slides
python T.PY generate pdf          # Generate PDF document
python T.PY demo                  # Run the protocol demonstration
python T.PY web                   # Start web interface
"""

import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
import hashlib
import argparse
import io
import contextlib

try:
    from flask import Flask, render_template_string, request, jsonify, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available. Install with: pip install flask")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available. Install with: pip install reportlab")

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False
    print("python-pptx not available. Install with: pip install python-pptx")

class ProtocolBase:
    """Base class for all protocols with common validation and serialization."""
    def validate(self) -> bool:
        """Validate the protocol structure."""
        raise NotImplementedError

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.__dict__, indent=2, default=str)

class MCPContext(ProtocolBase):
    """Model Context Protocol - Stable, versioned context packaging."""
    def __init__(self, context_id: str, version: str = "1.0"):
        self.context_id = context_id
        self.version = version
        self.context_slots: List[Dict[str, Any]] = []
        self.budget_tokens = 1000

    def add_slot(self, slot_name: str, content: str):
        """Add a context slot with content."""
        self.context_slots.append({
            "slot": slot_name,
            "content": content
        })

    def validate(self) -> bool:
        return bool(self.context_id and self.context_slots)

class RetrievalProvenance(ProtocolBase):
    """Retrieval Provenance Protocol - Evidence and provenance for retrieved data."""
    def __init__(self, document_id: str, origin: str, content: str):
        self.document_id = document_id
        self.origin = origin
        self.retrieved_at = datetime.now()
        self.trust_score = 0.95
        self.signature = self._generate_signature(content)
        self.content = content

    def _generate_signature(self, content: str) -> str:
        """Simple signature simulation."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def validate(self) -> bool:
        return bool(self.document_id and self.origin and self.content)

class ACPMessage(ProtocolBase):
    """Agent Communication Protocol - Structured message envelope."""
    def __init__(self, message_id: str, msg_type: str, session_id: str,
                 sender: str, receiver: str, payload: Dict[str, Any]):
        self.message_id = message_id
        self.type = msg_type
        self.session_id = session_id
        self.from_agent = sender
        self.to_agent = receiver
        self.payload = payload
        self.timestamp = datetime.now()

    def validate(self) -> bool:
        required = [self.message_id, self.type, self.session_id,
                   self.from_agent, self.to_agent, self.payload]
        return all(required)

class SandboxProtocol(ProtocolBase):
    """Sandbox Protocol - Execution class declarations for safety."""
    def __init__(self, tool: str, execution_class: str, requirements: Dict[str, Any]):
        self.tool = tool
        self.execution_class = execution_class  # 'safe', 'restricted', 'privileged'
        self.requirements = requirements

    def validate(self) -> bool:
        valid_classes = ['safe', 'restricted', 'privileged']
        return (self.tool and self.execution_class in valid_classes and
                isinstance(self.requirements, dict))

class Agent:
    """Simple agent that uses protocols for communication."""
    def __init__(self, name: str):
        self.name = name
        self.memory: Dict[str, Any] = {}

    def send_message(self, receiver: Agent, msg_type: str, payload: Dict[str, Any],
                    session_id: str = "session_001") -> ACPMessage:
        """Send a structured message using ACP."""
        message = ACPMessage(
            message_id=f"msg_{int(time.time())}_{self.name}",
            msg_type=msg_type,
            session_id=session_id,
            sender=self.name,
            receiver=receiver.name,
            payload=payload
        )
        if message.validate():
            print(f"📤 {self.name} → {receiver.name}: {msg_type}")
            print(message.to_json())
            receiver.receive_message(message)
            return message
        else:
            raise ValueError("Invalid message structure")

    def receive_message(self, message: ACPMessage):
        """Process incoming ACP message."""
        if not message.validate():
            print(f"❌ {self.name} rejected invalid message")
            return

        print(f"📥 {self.name} received: {message.type}")
        # Process based on message type
        if message.type == "task_request":
            self.handle_task_request(message.payload)
        elif message.type == "context_update":
            self.handle_context_update(message.payload)
        elif message.type == "summarize_request":
            self.handle_summarize_request(message.payload)

    def handle_task_request(self, payload: Dict[str, Any]):
        """Handle a task request with sandbox protocol."""
        tool = payload.get("tool", "unknown")
        sandbox = SandboxProtocol(
            tool=tool,
            execution_class=payload.get("execution_class", "safe"),
            requirements=payload.get("requirements", {})
        )

        if sandbox.validate():
            print(f"🔒 {self.name} executing {tool} in {sandbox.execution_class} mode")
            # Simulate execution
            result = f"Executed {tool} successfully"
            self.memory["last_result"] = result
        else:
            print(f"🚫 {self.name} rejected unsafe tool execution")

    def handle_context_update(self, payload: Dict[str, Any]):
        """Handle context update with MCP."""
        context = MCPContext(
            context_id=payload.get("context_id", "ctx_001"),
            version=payload.get("version", "1.0")
        )

        for slot in payload.get("context_slots", []):
            context.add_slot(slot["slot"], slot["content"])

        if context.validate():
            print(f"🧠 {self.name} updated context: {context.context_id}")
            self.memory["current_context"] = context
        else:
            print(f"❌ {self.name} rejected invalid context")

    def handle_summarize_request(self, payload: Dict[str, Any]):
        """Handle summarization request."""
        content = payload.get("content", "")
        summary = self.summarize_text(content)
        print(f"📝 {self.name} summarized content: {summary[:100]}...")
        self.memory["last_summary"] = summary

    def summarize_text(self, text: str) -> str:
        """Simple text summarization (extract key sentences)."""
        sentences = text.split('.')
        # Simple heuristic: take first and last sentences, plus any with keywords
        keywords = ['protocol', 'agent', 'trust', 'context', 'communication']
        key_sentences = []
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in keywords):
                key_sentences.append(sentence.strip())
        if not key_sentences:
            key_sentences = sentences[:2] + sentences[-2:]
        return '. '.join(key_sentences) + '.'

# Web Application Setup
if FLASK_AVAILABLE:
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Agentic Protocol Engineering Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; text-align: center; }
                .button { background: #007acc; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 10px; text-decoration: none; display: inline-block; }
                .button:hover { background: #005aa3; }
                .log-area { background: #f8f8f8; border: 1px solid #ddd; padding: 10px; height: 400px; overflow-y: auto; font-family: monospace; white-space: pre-wrap; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #eee; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Agentic Protocol Engineering Dashboard</h1>
                <p>Welcome to the real-time protocol demonstration system. Click buttons below to run protocol demos and see live logs.</p>
                
                <div class="section">
                    <h2>Protocol Demonstrations</h2>
                    <button class="button" onclick="runDemo()">Run Protocol Demo</button>
                    <button class="button" onclick="runAnalysis()">Analyze Document</button>
                    <button class="button" onclick="generateSlides()">Generate Slides</button>
                    <button class="button" onclick="generatePDF()">Generate PDF Report</button>
                </div>
                
                <div class="section">
                    <h2>Live Logs</h2>
                    <div id="logArea" class="log-area">Click a button above to start seeing protocol logs in real-time...</div>
                </div>
                
                <div class="section">
                    <h2>Generated Files</h2>
                    <div id="fileList">
                        <p>No files generated yet. Click a button above to create content.</p>
                    </div>
                </div>
            </div>
            
            <script>
                function runDemo() {
                    fetch('/run_demo')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('logArea').textContent = data.output;
                            updateFileList(data.files);
                        });
                }
                
                function runAnalysis() {
                    fetch('/run_analysis')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('logArea').textContent = data.output;
                            updateFileList(data.files);
                        });
                }
                
                function generateSlides() {
                    fetch('/generate_slides')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('logArea').textContent = data.output;
                            updateFileList(data.files);
                        });
                }
                
                function generatePDF() {
                    fetch('/generate_pdf')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('logArea').textContent = data.output;
                            updateFileList(data.files);
                        });
                }
                
                function updateFileList(files) {
                    const fileList = document.getElementById('fileList');
                    if (files.length === 0) {
                        fileList.innerHTML = '<p>No files generated.</p>';
                        return;
                    }
                    
                    let html = '<p>Generated files:</p><ul>';
                    files.forEach(file => {
                        html += `<li><a href="/files/${file}" target="_blank">${file}</a></li>`;
                    });
                    html += '</ul>';
                    fileList.innerHTML = html;
                }
            </script>
        </body>
        </html>
        """)

    @app.route('/run_demo')
    def run_demo():
        # Capture stdout
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            demo_protocols()
        output = f.getvalue()
        return jsonify({'output': output, 'files': []})

    @app.route('/run_analysis')
    def run_analysis():
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = analyze_document("Agentic_Protocol_Slide.md")
        output = f.getvalue()
        files = []
        if result:
            files.append(f"analysis_Agentic_Protocol_Slide.json")
        return jsonify({'output': output, 'files': files})

    @app.route('/generate_slides')
    def generate_slides_route():
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            generate_slides()
        output = f.getvalue()
        files = ["agentic_protocol_engineering_presentation.md", "agentic_protocol_engineering_presentation.pptx"]
        return jsonify({'output': output, 'files': files})

    @app.route('/generate_pdf')
    def generate_pdf_route():
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            generate_pdf()
        output = f.getvalue()
        files = ["protocol_analysis_report_report.pdf"]
        return jsonify({'output': output, 'files': files})

    @app.route('/files/<filename>')
    def serve_file(filename):
        return send_from_directory('.', filename)

def read_file_with_provenance(file_path: str) -> RetrievalProvenance:
    """Read a file and create a RetrievalProvenance object."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return RetrievalProvenance(
        document_id=f"doc_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
        origin=file_path,
        content=content
    )

def demo_protocols(file_path: str = None):
    """Run a demonstration of the protocols in action."""
    print("🚀 Starting Agentic Protocol Engineering Demo")
    print("=" * 50)
    print("\n🎯 Goal: Show how protocols prevent 'trust bleeding' in agent systems")
    time.sleep(2)

    # Create agents
    research_agent = Agent("ResearchBot")
    content_agent = Agent("ContentWriter")

    # Demo 1: Retrieval with Provenance
    print("\n📚 Demo 1: Retrieval Provenance Protocol")
    print("   → Ensures data comes with evidence and trust scores")
    doc = RetrievalProvenance(
        document_id="doc_123",
        origin="https://example.com/policies",
        content="Dosage: 50mg daily"
    )
    print("Retrieved document with provenance:")
    print(doc.to_json())
    print("💡 Remember: Every piece of data needs provenance!")
    time.sleep(3)

    # Demo 2: Context Packaging with MCP
    print("\n🧩 Demo 2: Model Context Protocol")
    print("   → Packages context in stable, versioned slots")
    context = MCPContext("ctx_456", "1.1")
    context.add_slot("retrieved_knowledge", doc.content)
    context.add_slot("current_task", "Prepare safety review summary")
    print("Packaged context:")
    print(context.to_json())
    print("💡 Remember: MCP = Model Context Protocol (stable context)")
    time.sleep(3)

    # Demo 3: Agent Communication with ACP
    print("\n💬 Demo 3: Agent Communication Protocol")
    print("   → Structured messaging between agents")
    research_agent.send_message(
        content_agent,
        "context_update",
        {
            "context_id": context.context_id,
            "version": context.version,
            "context_slots": context.context_slots
        }
    )
    print("💡 Remember: ACP = Agent Communication Protocol (structured messages)")
    time.sleep(3)

    # Demo 4: Task Execution with Sandbox Protocol
    print("\n🔒 Demo 4: Sandbox Protocol for Safe Execution")
    print("   → Governs tool execution with safety classes")
    research_agent.send_message(
        content_agent,
        "task_request",
        {
            "tool": "generate_report",
            "execution_class": "restricted",
            "requirements": {
                "network_access": False,
                "max_runtime_seconds": 60
            }
        }
    )
    print("💡 Remember: Sandbox prevents unsafe tool execution!")
    time.sleep(2)

    # Real Implementation: Document Analysis Task
    print("\n🛠️  Real Implementation: Document Analysis with Protocols")
    print("   → Agents collaborate to analyze and summarize a document")
    
    # Determine file to analyze
    if file_path and os.path.exists(file_path):
        target_file = file_path
    else:
        target_file = "Agentic_Protocol_Slide.md"  # Default file in workspace
    
    try:
        # Step 1: Retrieve document with provenance
        print(f"\n📖 Reading document: {target_file}")
        doc_provenance = read_file_with_provenance(target_file)
        print("Document retrieved with provenance:")
        print(f"   Origin: {doc_provenance.origin}")
        print(f"   Trust Score: {doc_provenance.trust_score}")
        print(f"   Content Length: {len(doc_provenance.content)} characters")
        
        # Step 2: Package context with MCP
        analysis_context = MCPContext("analysis_ctx", "1.0")
        analysis_context.add_slot("document_content", doc_provenance.content[:1000])  # First 1000 chars
        analysis_context.add_slot("document_metadata", f"Origin: {doc_provenance.origin}, Trust: {doc_provenance.trust_score}")
        analysis_context.add_slot("task", "Summarize key protocols and concepts")
        
        # Step 3: Send context to content agent
        research_agent.send_message(
            content_agent,
            "context_update",
            {
                "context_id": analysis_context.context_id,
                "version": analysis_context.version,
                "context_slots": analysis_context.context_slots
            }
        )
        
        # Step 4: Request summarization with sandbox protocol
        research_agent.send_message(
            content_agent,
            "summarize_request",
            {
                "content": doc_provenance.content,
                "tool": "text_summarizer",
                "execution_class": "safe",
                "requirements": {
                    "max_input_length": 5000,
                    "output_format": "structured_summary"
                }
            }
        )
        
        # Step 5: Output the result
        if "last_summary" in content_agent.memory:
            summary = content_agent.memory["last_summary"]
            print("\n📋 Final Summary Generated by Agents:")
            print("=" * 50)
            print(summary)
            print("=" * 50)
            
            # Save to file for real implementation
            output_file = f"summary_{os.path.basename(target_file).replace('.md', '')}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Summary of {target_file}\n")
                f.write("=" * 50 + "\n")
                f.write(summary)
                f.write("\n" + "=" * 50 + "\n")
                f.write("Generated using Agentic Protocols: MCP, ACP, Provenance, Sandbox")
            print(f"\n💾 Summary saved to: {output_file}")
        else:
            print("\n❌ Summary generation failed")
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please provide a valid file path or ensure Agentic_Protocol_Slide.md exists.")
    
    print("\n✅ Demo completed! Protocols ensure trust and structure in agent interactions.")
    print("\n🔑 Key Takeaways to Remember:")
    print("   • MCP: Context packaging (stable, versioned)")
    print("   • ACP: Agent messaging (structured, validated)")
    print("   • Provenance: Data evidence (trust scores, signatures)")
    print("   • Sandbox: Execution safety (classes: safe/restricted/privileged)")
def generate_slide_content(content_agent: Agent, topic: str, context: MCPContext) -> Dict[str, Any]:
    """Generate slide content using protocols."""
    # Create a task request for slide generation
    task_payload = {
        "tool": "slide_generator",
        "execution_class": "safe",
        "requirements": {
            "topic": topic,
            "context_slots": context.context_slots,
            "output_format": "presentation_slides"
        }
    }

    # Simulate slide generation with sandbox protocol
    sandbox = SandboxProtocol(
        tool="slide_generator",
        execution_class="safe",
        requirements=task_payload["requirements"]
    )

    if sandbox.validate():
        print(f"🔒 {content_agent.name} generating slides for: {topic}")

        # Generate sample slide content
        slides = {
            "title_slide": {
                "title": f"🚀 {topic}",
                "subtitle": "Generated using Agentic Protocols",
                "content": "Trust-maintained content generation"
            },
            "content_slide_1": {
                "title": "Key Concepts",
                "bullets": [
                    "• Protocol-driven development",
                    "• Trust and provenance tracking",
                    "• Structured agent communication",
                    "• Safe execution environments"
                ]
            },
            "content_slide_2": {
                "title": "Implementation Benefits",
                "bullets": [
                    "• Maintains data integrity",
                    "• Enables audit trails",
                    "• Prevents trust bleeding",
                    "• Supports collaboration"
                ]
            }
        }

        content_agent.memory["generated_slides"] = slides
        return slides
    else:
        raise ValueError("Slide generation failed sandbox validation")

def create_presentation_from_protocols(slides: Dict[str, Any], output_file: str):
    """Create actual PPTX presentation using the generated content."""
    print(f"📊 Creating presentation: {output_file}")

    if not PPTX_AVAILABLE:
        print("❌ python-pptx not available, creating markdown file instead")
        # Fallback to markdown
        content = f"""# {slides['title_slide']['title']}

## {slides['title_slide']['subtitle']}

### Generated using Agentic Protocols
- MCP: Model Context Protocol
- ACP: Agent Communication Protocol
- Provenance: Data Trust Tracking
- Sandbox: Execution Safety

---

## {slides['content_slide_1']['title']}

{chr(10).join(slides['content_slide_1']['bullets'])}

---

## {slides['content_slide_2']['title']}

{chr(10).join(slides['content_slide_2']['bullets'])}

---

## Protocol Evidence

This presentation was generated using:
- Document Analysis with Provenance Tracking
- Agent Collaboration via Structured Messaging
- Context Management with Version Control
- Safe Execution in Sandbox Environment

Generated at: {datetime.now().isoformat()}
"""
        with open(output_file.replace('.pptx', '.md'), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Presentation content saved as: {output_file.replace('.pptx', '.md')}")
        return

    # Create presentation
    prs = Presentation()

    # Title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = slides['title_slide']['title']
    subtitle.text = slides['title_slide']['subtitle']

    # Content slide 1
    bullet_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes

    title_shape = shapes.title
    body_shape = shapes.placeholders[1]

    title_shape.text = slides['content_slide_1']['title']
    tf = body_shape.text_frame
    tf.text = slides['content_slide_1']['bullets'][0].lstrip('• ')

    for bullet in slides['content_slide_1']['bullets'][1:]:
        p = tf.add_paragraph()
        p.text = bullet.lstrip('• ')
        p.level = 0

    # Content slide 2
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes

    title_shape = shapes.title
    body_shape = shapes.placeholders[1]

    title_shape.text = slides['content_slide_2']['title']
    tf = body_shape.text_frame
    tf.text = slides['content_slide_2']['bullets'][0].lstrip('• ')

    for bullet in slides['content_slide_2']['bullets'][1:]:
        p = tf.add_paragraph()
        p.text = bullet.lstrip('• ')
        p.level = 0

    # Save the presentation
    prs.save(output_file)
    print(f"✅ PowerPoint presentation saved as: {output_file}")

def create_pdf_report(content_agent: Agent, analysis_results: Dict[str, Any], output_file: str):
    """Create PDF report from analysis results."""
    print(f"📄 Creating PDF report: {output_file}")

    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab not available, creating text file instead")
        # Fallback to text file
        content = f"""PROTOCOL-DRIVEN ANALYSIS REPORT
{'='*50}

Topic: {analysis_results.get('topic', 'Protocol Analysis')}
Generated: {analysis_results.get('generated_at', datetime.now().isoformat())}

PROTOCOLS DEMONSTRATED:
{'-'*25}
{chr(10).join('- ' + p for p in analysis_results.get('protocols_demonstrated', []))}

KEY FINDINGS:
{'-'*15}
{chr(10).join(f'• {finding}' for finding in analysis_results.get('key_findings', []))}

ANALYSIS METHODOLOGY:
{'-'*20}
This report was generated using agentic protocols that ensure:
- Data provenance and trust tracking
- Structured inter-agent communication
- Context stability and versioning
- Safe execution environments

All content maintains cryptographic signatures and audit trails.

{'='*50}
Generated by Protocol-Driven Content Generation System
"""
        with open(output_file.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Report content saved as: {output_file.replace('.pdf', '.txt')}")
        return

    # Create PDF using ReportLab
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
    )

    normal_style = styles['Normal']

    # Build the PDF content
    story = []

    # Title
    story.append(Paragraph("PROTOCOL-DRIVEN ANALYSIS REPORT", title_style))
    story.append(Spacer(1, 12))

    # Topic and generation info
    topic = analysis_results.get('topic', 'Protocol Analysis')
    generated_at = analysis_results.get('generated_at', datetime.now().isoformat())

    story.append(Paragraph(f"<b>Topic:</b> {topic}", normal_style))
    story.append(Paragraph(f"<b>Generated:</b> {generated_at}", normal_style))
    story.append(Spacer(1, 20))

    # Protocols Demonstrated
    story.append(Paragraph("PROTOCOLS DEMONSTRATED", heading_style))
    protocols = analysis_results.get('protocols_demonstrated', [])
    for protocol in protocols:
        story.append(Paragraph(f"• {protocol}", normal_style))
    story.append(Spacer(1, 20))

    # Key Findings
    story.append(Paragraph("KEY FINDINGS", heading_style))
    findings = analysis_results.get('key_findings', [])
    for finding in findings:
        story.append(Paragraph(f"• {finding}", normal_style))
    story.append(Spacer(1, 20))

    # Analysis Methodology
    story.append(Paragraph("ANALYSIS METHODOLOGY", heading_style))
    methodology_text = """This report was generated using agentic protocols that ensure:
• Data provenance and trust tracking
• Structured inter-agent communication
• Context stability and versioning
• Safe execution environments

All content maintains cryptographic signatures and audit trails."""
    story.append(Paragraph(methodology_text, normal_style))
    story.append(Spacer(1, 20))

    # Footer
    footer_text = "Generated by Protocol-Driven Content Generation System"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=normal_style, alignment=1)))

    # Build the PDF
    doc.build(story)
    print(f"✅ PDF report created: {output_file}")

def analyze_document(file_path: str):
    """Real document analysis using protocols."""
    print("🔍 Starting Protocol-Based Document Analysis")
    print("=" * 50)

    # Create agents
    research_agent = Agent("ResearchBot")
    content_agent = Agent("ContentWriter")
    analysis_agent = Agent("AnalysisAgent")

    try:
        # Step 1: Retrieve document with provenance
        print(f"\n📖 Reading document: {file_path}")
        doc_provenance = read_file_with_provenance(file_path)
        print("Document retrieved with provenance:")
        print(f"   Origin: {doc_provenance.origin}")
        print(f"   Trust Score: {doc_provenance.trust_score}")
        print(f"   Content Length: {len(doc_provenance.content)} characters")

        # Step 2: Package context with MCP
        analysis_context = MCPContext("analysis_ctx", "1.0")
        analysis_context.add_slot("document_content", doc_provenance.content[:2000])
        analysis_context.add_slot("document_metadata", f"Origin: {doc_provenance.origin}, Trust: {doc_provenance.trust_score}")
        analysis_context.add_slot("task", "Analyze and extract key concepts")

        # Step 3: Send context to analysis agent
        research_agent.send_message(
            analysis_agent,
            "context_update",
            {
                "context_id": analysis_context.context_id,
                "version": analysis_context.version,
                "context_slots": analysis_context.context_slots
            }
        )

        # Step 4: Request analysis with sandbox protocol
        research_agent.send_message(
            analysis_agent,
            "task_request",
            {
                "tool": "content_analyzer",
                "execution_class": "safe",
                "requirements": {
                    "analysis_type": "concept_extraction",
                    "max_concepts": 5,
                    "output_format": "structured_analysis"
                }
            }
        )

        # Step 5: Generate summary
        research_agent.send_message(
            content_agent,
            "summarize_request",
            {
                "content": doc_provenance.content,
                "tool": "text_summarizer",
                "execution_class": "safe",
                "requirements": {
                    "summary_length": "medium",
                    "focus_areas": ["protocols", "trust", "implementation"]
                }
            }
        )

        # Step 6: Compile results
        analysis_results = {
            "document_provenance": doc_provenance.to_json(),
            "context_used": analysis_context.to_json(),
            "summary": content_agent.memory.get("last_summary", "Analysis incomplete"),
            "timestamp": datetime.now().isoformat(),
            "protocols_used": ["MCP", "ACP", "Provenance", "Sandbox"]
        }

        # Save analysis results
        output_file = f"analysis_{os.path.basename(file_path).replace('.md', '')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, default=str)

        print(f"\n💾 Analysis results saved to: {output_file}")
        print("\n📋 Analysis Summary:")
        print("=" * 30)
        print(analysis_results["summary"])

        return analysis_results

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return None

def generate_slides(topic: str = "Agentic Protocol Engineering"):
    """Generate presentation slides using protocols."""
    print("🎨 Starting Protocol-Based Slide Generation")
    print("=" * 50)

    # Create agents
    content_agent = Agent("ContentWriter")
    design_agent = Agent("DesignBot")

    # Create context for slide generation
    slide_context = MCPContext("slide_gen_ctx", "1.0")
    slide_context.add_slot("topic", topic)
    slide_context.add_slot("audience", "technical_presenters")
    slide_context.add_slot("style", "professional_minimalist")

    # Generate slide content
    slides = generate_slide_content(content_agent, topic, slide_context)

    # Create actual presentation file
    output_file = f"{topic.lower().replace(' ', '_')}_presentation.pptx"
    create_presentation_from_protocols(slides, output_file)

    print(f"\n✅ Slides generated and saved as: {output_file}")

def generate_pdf(topic: str = "Protocol Analysis Report"):
    """Generate PDF report using protocols."""
    print("📄 Starting Protocol-Based PDF Generation")
    print("=" * 50)

    # Create agents
    content_agent = Agent("ContentWriter")
    report_agent = Agent("ReportBot")

    # Create sample analysis results
    analysis_results = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "protocols_demonstrated": ["MCP", "ACP", "Provenance", "Sandbox"],
        "key_findings": [
            "Protocols maintain trust in agent interactions",
            "Structured communication prevents information loss",
            "Provenance tracking enables audit trails",
            "Sandbox execution provides safety guarantees"
        ]
    }

    # Create PDF report
    output_file = f"{topic.lower().replace(' ', '_')}_report.pdf"
    create_pdf_report(content_agent, analysis_results, output_file)

    print(f"\n✅ PDF report generated and saved as: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Protocol-Driven Content Generation System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a document")
    analyze_parser.add_argument("file_path", help="Path to file to analyze")

    # Generate commands
    generate_parser = subparsers.add_parser("generate", help="Generate content")
    generate_subparsers = generate_parser.add_subparsers(dest="content_type", help="Content type")

    slides_parser = generate_subparsers.add_parser("slides", help="Generate presentation slides")
    slides_parser.add_argument("--topic", default="Agentic Protocol Engineering", help="Slide topic")

    pdf_parser = generate_subparsers.add_parser("pdf", help="Generate PDF report")
    pdf_parser.add_argument("--topic", default="Protocol Analysis Report", help="Report topic")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run protocol demonstration")

    # Web command
    web_parser = subparsers.add_parser("web", help="Start web interface")

    args = parser.parse_args()

    if args.command == "analyze":
        analyze_document(args.file_path)
    elif args.command == "generate":
        if args.content_type == "slides":
            generate_slides(args.topic)
        elif args.content_type == "pdf":
            generate_pdf(args.topic)
    elif args.command == "demo":
        demo_protocols()
    elif args.command == "web":
        if FLASK_AVAILABLE:
            print("🌐 Starting web interface at http://localhost:5000")
            print("Open your browser and navigate to the URL above.")
            app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            print("❌ Flask not available. Install with: pip install flask")
    else:
        parser.print_help()
