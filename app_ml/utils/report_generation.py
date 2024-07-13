import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
import matplotlib
matplotlib.use('agg')  # Configurar matplotlib para utilizar el backend 'agg'
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def generate_report(results, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='CenteredTitle', parent=styles['Heading1'], alignment=1)
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    elements.append(Paragraph("Informe comparativo de aprendizaje automático", title_style))
    elements.append(Paragraph(f"Reporte generado el {now}", normal_style))

    for algorithm, metrics in results.items():
        elements.append(Paragraph(f"Results for {algorithm}", subtitle_style))
        
        data = [
            ["Metric", "Value"],
            ["Accuracy", f"{metrics['accuracy']:.4f}"],
            ["Precision", f"{metrics['precision']:.4f}"],
            ["Recall", f"{metrics['recall']:.4f}"],
            ["F1 Score", f"{metrics['f1_score']:.4f}"],
            ["AUC", f"{metrics['auc']:.4f}"],
            ["Uso CPU", f"{metrics['cpu_usage']:.2f}%"],
            ["Tiempo Ejecución", f"{metrics['execution_time']:.2f} seconds"]
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
    title_style = ParagraphStyle(name='CenteredTitle', parent=styles['Heading1'], alignment=1)
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    elements.append(Paragraph("Comparación de algoritmos de aprendizaje automático", title_style))
    elements.append(Paragraph(f"Reporte generado el {now} <br/>", normal_style))

    # Create the comparison table
    data = [["Algoritmo", "Accuracy", "Precision", "Recall", "F1 Score", "AUC", "Uso CPU", "Tiempo E."]]
    
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
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Create bar charts for each metric
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'cpu_usage', 'execution_time']
    
    for metric in metrics:
        plt.figure(figsize=(8, 4))
        algorithms = list(results.keys())
        values = [results[alg][metric] for alg in algorithms]
        
        bars = plt.bar(algorithms, values)
        plt.title(f'Comparación de {metric.replace("_", " ").title()}')
        plt.xlabel('Algoritmos')
        plt.ylabel(metric.replace("_", " ").title())
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Adding value labels on top of the bars
        for bar, value in zip(bars, values):
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, f'{value:.4f}', ha='center', va='bottom')
        
        # Save the plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Add the plot to the PDF
        img = Image(buf)
        img.drawHeight = 300
        img.drawWidth = 500
        elements.append(img)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        
        plt.close()

    doc.build(elements)
