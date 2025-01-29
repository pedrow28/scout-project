#!/usr/bin/env python
import sys
import warnings
import os
import markdown
import pdfkit

from src.crew import ScoutCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
def clean_markdown_code_blocks(input_md_file, output_md_file):
    with open(input_md_file, 'r', encoding='utf-8') as md_file:
        lines = md_file.readlines()
    
    cleaned_lines = []
    inside_code_block = False
    
    for line in lines:
        # Verifica se é o início ou fim de um bloco de código
        if line.strip().startswith("```"):
            inside_code_block = not inside_code_block
            continue  # Pula a linha que contém ```
        cleaned_lines.append(line)
    
    # Salva o resultado no arquivo de saída
    with open(output_md_file, 'w', encoding='utf-8') as output_file:
        output_file.writelines(cleaned_lines)
    
    print(f"Arquivo Markdown limpo salvo em: {output_md_file}")




def render_markdown_to_pdf(input_md_file, output_pdf_file):
    path_whtml = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
    
    # Ler o arquivo Markdown
    with open(input_md_file, 'r', encoding='utf-8') as md_file:
        md_content = md_file.read()
    
    # Converter Markdown para HTML com suporte a blocos de código
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])
    
    # Adicionar estilo CSS para formatação
    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
            }}
            h1, h2, h3 {{
                color: #333;
            }}
            pre, code {{
                background-color: #f4f4f4;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
                font-family: Consolas, 'Courier New', monospace;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            th {{
                background-color: #f4f4f4;
                font-weight: bold;
            }}
            td {{
                text-align: left;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Configurar pdfkit
    options = {
        'encoding': 'UTF-8',
        'enable-local-file-access': None,
    }
    
    # Caminho para o arquivo PDF
    path_pdf = f"output/{output_pdf_file}.pdf"
    
    # Configurar caminho explicitamente
    config = pdfkit.configuration(wkhtmltopdf=path_whtml)
    
    # Gerar o PDF a partir do HTML
    pdfkit.from_string(html_template, path_pdf, options=options, configuration=config)
    print(f"PDF gerado: {path_pdf}")

def run():
    """
    Run the crew.
    """

    user_input = input("Insira a pesquisa a ser feita: ")

    inputs = {
        'topic': user_input
    }
    ScoutCrew().crew().kickoff(inputs=inputs)

    nome_pdf = input("Insira o nome do relatório: ")

    clean_markdown_code_blocks("output/report.md", "output/report_cleaned.md") ## Necessário ajustar

    render_markdown_to_pdf("output/report_cleaned.md", nome_pdf) ## Necessário ajustar



if __name__ == "__main__":
    run()

