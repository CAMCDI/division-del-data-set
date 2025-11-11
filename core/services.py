import pandas as pd
import os
from sklearn.model_selection import train_test_split

# IMPORTANTE: Configurar matplotlib sin backend gráfico
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def load_arff_dataset_robust(data_path):
    """Cargador robusto de ARFF que maneja diferentes formatos"""
    try:
        with open(data_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        # Buscar secciones
        lines = content.split('\n')
        attributes = []
        data_start = None
        data_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Ignorar líneas vacías y comentarios
            if not line or line.startswith('%'):
                continue
                
            # Procesar atributos
            if line.lower().startswith('@attribute'):
                # Manejar diferentes formatos de atributo
                parts = line.split()
                if len(parts) >= 2:
                    attr_name = parts[1]
                    # Limpiar el nombre del atributo
                    attr_name = attr_name.strip("'\"")
                    attributes.append(attr_name)
            
            # Encontrar inicio de datos
            elif line.lower().startswith('@data'):
                data_start = i + 1
                break
        
        # Si no encontramos @data, buscar desde el final
        if data_start is None:
            data_start = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.lower().startswith('@') and not line.startswith('%'):
                    data_start = i
                    break
        
        # Procesar datos
        for line in lines[data_start:]:
            line = line.strip()
            if line and not line.startswith('%'):
                # Limpiar la línea de datos
                line = line.split('%')[0].strip()  # Remover comentarios al final
                if line:
                    data_lines.append(line)
        
        # Si no pudimos obtener atributos, inferirlos de los datos
        if not attributes and data_lines:
            # Contar columnas basado en la primera línea de datos
            first_line = data_lines[0]
            num_columns = len(first_line.split(','))
            attributes = [f'col_{i}' for i in range(num_columns)]
        
        # Parsear datos
        data = []
        for line in data_lines:
            try:
                # Manejar diferentes formatos de datos
                values = line.split(',')
                if len(values) == len(attributes):
                    cleaned_values = []
                    for v in values:
                        v = v.strip()
                        # Remover comillas si existen
                        v = v.strip("'\"")
                        # Intentar convertir a número si es posible
                        try:
                            if '.' in v:
                                v = float(v)
                            else:
                                v = int(v)
                        except ValueError:
                            # Mantener como string si no se puede convertir
                            pass
                        cleaned_values.append(v)
                    data.append(cleaned_values)
            except Exception as e:
                print(f"Error parseando línea: {line}, error: {e}")
                continue
        
        if not data:
            raise ValueError("No se pudieron parsear datos del archivo ARFF")
        
        return pd.DataFrame(data, columns=attributes)
        
    except Exception as e:
        raise ValueError(f"Error cargando archivo ARFF: {str(e)}")

def train_val_test_split(df, rstate=42, shuffle=True, stratify=None):
    """Función EXACTA del notebook"""
    strat = df[stratify] if stratify and stratify in df.columns else None
    train_set, test_set = train_test_split(
        df, test_size=0.4, random_state=rstate, shuffle=shuffle, stratify=strat)
    strat = test_set[stratify] if stratify and stratify in test_set.columns else None
    val_set, test_set = train_test_split(
        test_set, test_size=0.5, random_state=rstate, shuffle=shuffle, stratify=strat)
    return (train_set, val_set, test_set)

def create_histogram_exact(df, column_name, title):
    """Crear histograma EXACTO como en el notebook - simple y directo"""
    try:
        # Configuración EXACTA como el notebook
        plt.figure(figsize=(10, 6))
        
        # Verificar si la columna existe
        if column_name not in df.columns:
            return None
            
        # Crear histograma SIMPLE como en el notebook
        # En el notebook solo hace: df['protocol_type'].hist()
        df[column_name].hist()
        
        plt.title(title)
        plt.xlabel(column_name)
        plt.ylabel('Frecuencia')
        plt.grid(True)
        plt.tight_layout()
        
        # Convertir a base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{graphic}"
        
    except Exception as e:
        print(f"Error creando histograma exacto para {column_name}: {e}")
        return None

def get_dataset_info(df):
    """Obtener información del dataset"""
    categorical_cols = []
    numeric_cols = []
    
    for col in df.columns:
        if df[col].dtype == 'object':
            categorical_cols.append(col)
        else:
            numeric_cols.append(col)
    
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB",
        'categorical_columns': categorical_cols,
        'numeric_columns': numeric_cols,
        'column_names': list(df.columns),
        'sample_data': df.head(3).fillna('').to_dict('records')
    }

def find_best_stratify_column(df):
    """Encontrar automáticamente columnas como protocol_type"""
    # Buscar columnas que parezcan tipos de protocolo o categorías similares
    potential_columns = []
    
    for col in df.columns:
        if df[col].dtype == 'object':
            unique_values = df[col].unique()
            # Buscar columnas con valores como: tcp, udp, icmp, etc.
            if len(unique_values) <= 10:  # Pocas categorías
                # Verificar si los valores parecen tipos/categorías
                sample_values = [str(v).lower() for v in unique_values[:3]]
                protocol_like = any(any(keyword in str(v).lower() for keyword in 
                                      ['tcp', 'udp', 'icmp', 'type', 'protocol', 'category', 'class']) 
                                  for v in sample_values)
                
                if protocol_like or len(unique_values) <= 5:
                    potential_columns.append((col, len(unique_values)))
    
    # Ordenar por número de categorías (preferir menos categorías)
    if potential_columns:
        potential_columns.sort(key=lambda x: x[1])
        return potential_columns[0][0]
    
    # Si no encontramos, usar la primera columna categórica
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    if categorical_cols:
        return categorical_cols[0]
    
    return None

def get_column_distribution(df, column_name):
    """Obtener distribución de columna como en el notebook"""
    if column_name in df.columns:
        return df[column_name].value_counts().to_dict()
    return {}