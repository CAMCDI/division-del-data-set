# views.py
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from sklearn.model_selection import train_test_split
import numpy as np
import re

def robust_arff_parser(file_content):
    try:
        try:
            content = file_content.decode('utf-8')
        except:
            content = file_content.decode('latin-1')
        
        lines = content.split('\n')
        attributes = []
        data = []
        in_data_section = False
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('%'):
                continue
                
            if line.lower().startswith('@attribute'):
                match = re.match(r'@attribute\s+(\S+)\s+(.+)', line, re.IGNORECASE)
                if match:
                    attr_name = match.group(1)
                    attributes.append(attr_name)
                else:
                    parts = line.split()
                    if len(parts) >= 2:
                        attr_name = parts[1]
                        attributes.append(attr_name)
            
            elif line.upper().startswith('@DATA'):
                in_data_section = True
                continue
                
            elif in_data_section and line:
                line = line.strip()
                if line:
                    values = line.split(',')
                    if len(values) == len(attributes):
                        data.append(values)
                    elif len(values) > len(attributes):
                        data.append(values[:len(attributes)])
                    else:
                        padded_values = values + [None] * (len(attributes) - len(values))
                        data.append(padded_values)
        
        df = pd.DataFrame(data, columns=attributes)
        
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass
                
        return df
        
    except Exception as e:
        raise Exception(f"Error parsing ARFF: {str(e)}")

def train_val_test_split(df, rstate=42, shuffle=True, stratify=None):
    strat = df[stratify] if stratify else None 
    train_set, test_set = train_test_split(
        df, test_size=0.4, random_state=rstate, shuffle=shuffle, stratify=strat)
    strat = test_set[stratify] if stratify else None 
    val_set, test_set = train_test_split(
        test_set, test_size=0.5, random_state=rstate, shuffle=shuffle, stratify=strat)
    return (train_set, val_set, test_set)

def process_arff(request):
    if request.method == 'POST' and request.FILES.get('arff_file'):
        try:
            arff_file = request.FILES['arff_file']
            file_content = arff_file.read()
            
            df = robust_arff_parser(file_content)
            
            if len(df) == 0:
                return render(request, 'upload.html', {
                    'error': 'El dataset esta vacio o no se pudo procesar.'
                })
            
            stratify_column = None
            possible_stratify_columns = ['protocol_type', 'protocol-type', 'protocol', 'type', 'class', 'label']
            
            for col in possible_stratify_columns:
                if col in df.columns:
                    stratify_column = col
                    break
            
            if not stratify_column:
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    stratify_column = categorical_cols[0]
            
            train_set, val_set, test_set = train_val_test_split(df, stratify=stratify_column)
            
            def plot_to_base64():
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()
                return base64.b64encode(image_png).decode('utf-8')
            
            graphs = []
            
            if stratify_column and stratify_column in df.columns:
                plt.figure(figsize=(10, 6))
                df[stratify_column].value_counts().plot(kind='bar', color='#1a535c')
                plt.title(f'Dataset Completo - {stratify_column}')
                plt.xlabel(stratify_column)
                plt.ylabel('Frecuencia')
                plt.xticks(rotation=45)
                graphs.append(plot_to_base64())
                plt.close()
                
                plt.figure(figsize=(10, 6))
                train_set[stratify_column].value_counts().plot(kind='bar', color='#4ecdc4')
                plt.title(f'Conjunto de Entrenamiento - {stratify_column}')
                plt.xlabel(stratify_column)
                plt.ylabel('Frecuencia')
                plt.xticks(rotation=45)
                graphs.append(plot_to_base64())
                plt.close()
                
                plt.figure(figsize=(10, 6))
                val_set[stratify_column].value_counts().plot(kind='bar', color='#ff6b6b')
                plt.title(f'Conjunto de Validacion - {stratify_column}')
                plt.xlabel(stratify_column)
                plt.ylabel('Frecuencia')
                plt.xticks(rotation=45)
                graphs.append(plot_to_base64())
                plt.close()
                
                plt.figure(figsize=(10, 6))
                test_set[stratify_column].value_counts().plot(kind='bar', color='#ffe66d')
                plt.title(f'Conjunto de Prueba - {stratify_column}')
                plt.xlabel(stratify_column)
                plt.ylabel('Frecuencia')
                plt.xticks(rotation=45)
                graphs.append(plot_to_base64())
                plt.close()
            else:
                for title in ['Dataset Completo', 'Conjunto de Entrenamiento', 'Conjunto de Validacion', 'Conjunto de Prueba']:
                    plt.figure(figsize=(10, 6))
                    plt.text(0.5, 0.5, f'No se encontro columna categorica para visualizacion', 
                            ha='center', va='center', fontsize=12)
                    plt.title(title)
                    graphs.append(plot_to_base64())
                    plt.close()
            
            stats = {
                'original': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'numeric_cols': len(df.select_dtypes(include=[np.number]).columns),
                    'categorical_cols': len(df.select_dtypes(include=['object']).columns),
                },
                'train': {'rows': len(train_set)},
                'val': {'rows': len(val_set)},
                'test': {'rows': len(test_set)}
            }
            
            context = {
                'stats': stats,
                'columns': list(df.columns),
                'graph1': graphs[0],
                'graph2': graphs[1],
                'graph3': graphs[2],
                'graph4': graphs[3],
                'stratify_column': stratify_column,
                'success': True
            }
            
            return render(request, 'results.html', context)
            
        except Exception as e:
            error_msg = f"Error procesando archivo: {str(e)}"
            return render(request, 'upload.html', {'error': error_msg})
    
    return render(request, 'upload.html')

def upload_page(request):
    return render(request, 'upload.html')