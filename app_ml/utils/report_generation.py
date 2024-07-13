# app_ml/utils/report_generation.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(results, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']

    elements.append(Paragraph("Machine Learning Comparison Report", title_style))

    for algorithm, metrics in results.items():
        elements.append(Paragraph(f"Results for {algorithm}", subtitle_style))
        
        data = [
            ["Metric", "Value"],
            ["Accuracy", f"{metrics['accuracy']:.4f}"],
            ["Precision", f"{metrics['precision']:.4f}"],
            ["Recall", f"{metrics['recall']:.4f}"],
            ["F1 Score", f"{metrics['f1_score']:.4f}"],
            ["AUC", f"{metrics['auc']:.4f}"],
            ["CPU Usage", f"{metrics['cpu_usage']:.2f}%"],
            ["Execution Time", f"{metrics['execution_time']:.2f} seconds"]
        ]

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

    doc.build(elements)

def generate_comparison_report(results, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']

    elements.append(Paragraph("Machine Learning Algorithms Comparison", title_style))

    data = [["Algorithm", "Accuracy", "Precision", "Recall", "F1 Score", "AUC", "CPU Usage", "Execution Time"]]
    
    for algorithm, metrics in results.items():
        data.append([
            algorithm,
            f"{metrics['accuracy']:.4f}",
            f"{metrics['precision']:.4f}",
            f"{metrics['recall']:.4f}",
            f"{metrics['f1_score']:.4f}",
            f"{metrics['auc']:.4f}",
            f"{metrics['cpu_usage']:.2f}%",
            f"{metrics['execution_time']:.2f}s"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)

    doc.build(elements)