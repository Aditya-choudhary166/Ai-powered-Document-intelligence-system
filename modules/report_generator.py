from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from xml.sax.saxutils import escape

def build_pdf_report(documents, analysis):
    buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallBody",parent=styles["BodyText"],fontSize=9,leading=13,spaceAfter=6))
    story=[Paragraph("Document Intelligence Report",styles["Title"]),
           Paragraph("AI-powered business document analysis",styles["Italic"]),Spacer(1,14)]
    story.append(Paragraph("Uploaded documents",styles["Heading2"]))
    for d in documents:
        story.append(Paragraph(f"{escape(d['name'])} — {d['pages']} pages",styles["SmallBody"]))
    story.append(Spacer(1,8))
    if analysis:
        story.append(Paragraph("Executive summary",styles["Heading2"]))
        story.append(Paragraph(escape(str(analysis.get("summary","No summary available."))),styles["SmallBody"]))
        story.append(Paragraph("Key information",styles["Heading2"]))
        for item in analysis.get("key_information",[]): story.append(Paragraph("• "+escape(str(item)),styles["SmallBody"]))
        story.append(Paragraph("Potential risks",styles["Heading2"]))
        risks=analysis.get("risks",[])
        if risks:
            data=[["Level","Finding","Evidence / source"]]
            for r in risks:
                data.append([str(r.get("level","")),str(r.get("title","")),str(r.get("evidence",""))[:250]+" | "+str(r.get("source",""))+" p."+str(r.get("page",""))])
            t=Table(data,colWidths=[55,130,300],repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#172554")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                                   ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#CBD5E1")),("FONTSIZE",(0,0),(-1,-1),8),
                                   ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F1F5F9")])]))
            story.append(t)
        else: story.append(Paragraph("No risks returned.",styles["SmallBody"]))
        story.append(Paragraph("Recommended actions",styles["Heading2"]))
        for a in analysis.get("actions",[]):
            story.append(Paragraph(f"• {escape(str(a.get('task','')))} — Owner: {escape(str(a.get('owner','Unassigned')))}; Deadline: {escape(str(a.get('deadline','Not specified')))}; Priority: {escape(str(a.get('priority','Medium')))}",styles["SmallBody"]))
    else:
        story.append(Paragraph("AI analysis has not been run. This report lists uploaded documents only.",styles["SmallBody"]))
    story.append(Spacer(1,18))
    story.append(Paragraph("Disclaimer: AI-generated observations may be incomplete or incorrect. Verify all findings with a qualified reviewer. This report is not legal advice.",styles["SmallBody"]))
    doc.build(story)
    return buf.getvalue()
