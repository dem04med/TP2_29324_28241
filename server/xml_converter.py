import xml.etree.ElementTree as ET
from lxml import etree
import json
import logging
from datetime import datetime
import os
import csv
import pandas as pd
from io import StringIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XMLConverter:
    def __init__(self):
        self.xml_schemas_path = "/app/../data/xml_schemas"
        self.xml_outputs_path = "/app/../data/xml_outputs"
    
    def validate_xml(self, xml_content, schema_path=None):
        """Valida XML contra um schema XSD se fornecido"""
        try:
            if schema_path and os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as schema_file:
                    schema_doc = etree.parse(schema_file)
                    schema = etree.XMLSchema(schema_doc)
                    
                xml_doc = etree.fromstring(xml_content.encode('utf-8'))
                if schema.validate(xml_doc):
                    logger.info("XML válido de acordo com o schema")
                    return True, "XML válido"
                else:
                    errors = [str(error) for error in schema.error_log]
                    logger.warning(f"XML inválido: {errors}")
                    return False, errors
            else:
                # Validação básica de XML bem formado
                ET.fromstring(xml_content)
                logger.info("XML bem formado")
                return True, "XML bem formado"
                
        except ET.ParseError as e:
            logger.error(f"Erro de parsing XML: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return False, str(e)
    
    def xml_to_json(self, xml_content):
        """Converte XML para JSON"""
        try:
            def xml_to_dict(element):
                result = {}
                
                # Adicionar atributos
                if element.attrib:
                    result['@attributes'] = element.attrib
                
                # Adicionar texto se existir
                if element.text and element.text.strip():
                    if len(element) == 0:  # Elemento folha
                        return element.text.strip()
                    else:
                        result['#text'] = element.text.strip()
                
                # Processar elementos filhos
                for child in element:
                    child_data = xml_to_dict(child)
                    if child.tag in result:
                        # Se já existe, converter para lista
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
                
                return result
            
            root = ET.fromstring(xml_content)
            json_data = {root.tag: xml_to_dict(root)}
            
            logger.info("Conversão XML para JSON realizada com sucesso")
            return True, json.dumps(json_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Erro na conversão XML para JSON: {e}")
            return False, str(e)
    
    def json_to_xml(self, json_content, root_element_name="root"):
        """Converte JSON para XML"""
        try:
            def dict_to_xml(data, parent_element):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == '@attributes':
                            # Adicionar atributos ao elemento pai
                            for attr_key, attr_value in value.items():
                                parent_element.set(attr_key, str(attr_value))
                        elif key == '#text':
                            # Adicionar texto ao elemento pai
                            parent_element.text = str(value)
                        else:
                            # Criar elemento filho
                            child_element = ET.SubElement(parent_element, key)
                            dict_to_xml(value, child_element)
                elif isinstance(data, list):
                    for item in data:
                        dict_to_xml(item, parent_element)
                else:
                    # Valor simples
                    parent_element.text = str(data)
            
            json_data = json.loads(json_content)
            
            # Se o JSON tem uma chave raiz, usar essa chave
            if isinstance(json_data, dict) and len(json_data) == 1:
                root_key = list(json_data.keys())[0]
                root = ET.Element(root_key)
                dict_to_xml(json_data[root_key], root)
            else:
                root = ET.Element(root_element_name)
                dict_to_xml(json_data, root)
            
            # Converter para string com formatação
            xml_str = ET.tostring(root, encoding='unicode')
            
            # Formatar o XML usando lxml para melhor aparência
            formatted_xml = etree.tostring(
                etree.fromstring(xml_str), 
                pretty_print=True, 
                encoding='unicode'
            )
            
            logger.info("Conversão JSON para XML realizada com sucesso")
            return True, formatted_xml
            
        except Exception as e:
            logger.error(f"Erro na conversão JSON para XML: {e}")
            return False, str(e)
    
    def transform_xml(self, xml_content, xslt_path):
        """Aplica transformação XSLT ao XML"""
        try:
            if not os.path.exists(xslt_path):
                return False, f"Arquivo XSLT não encontrado: {xslt_path}"
            
            # Carregar XML e XSLT
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            xslt_doc = etree.parse(xslt_path)
            transform = etree.XSLT(xslt_doc)
            
            # Aplicar transformação
            result = transform(xml_doc)
            
            logger.info("Transformação XSLT aplicada com sucesso")
            return True, str(result)
            
        except Exception as e:
            logger.error(f"Erro na transformação XSLT: {e}")
            return False, str(e)
    
    def csv_to_xml(self, csv_content, root_element="dataset", row_element="record"):
        """Converte CSV para XML estruturado"""
        try:
            # Ler CSV usando pandas para melhor manipulação
            df = pd.read_csv(StringIO(csv_content))
            
            # Criar elemento raiz
            root = ET.Element(root_element)
            root.set("source", "kaggle")
            root.set("generated", datetime.now().isoformat())
            root.set("records", str(len(df)))
            
            # Adicionar metadados
            metadata = ET.SubElement(root, "metadata")
            columns = ET.SubElement(metadata, "columns")
            
            for col in df.columns:
                col_elem = ET.SubElement(columns, "column")
                col_elem.set("name", str(col))
                col_elem.set("type", str(df[col].dtype))
                col_elem.set("non_null", str(df[col].notna().sum()))
            
            # Adicionar dados
            data_elem = ET.SubElement(root, "data")
            
            for index, row in df.iterrows():
                record = ET.SubElement(data_elem, row_element)
                record.set("id", str(index))
                
                for col in df.columns:
                    field = ET.SubElement(record, self._clean_column_name(col))
                    value = row[col]
                    
                    if pd.isna(value):
                        field.set("null", "true")
                        field.text = ""
                    else:
                        field.text = str(value)
            
            # Converter para string formatada
            xml_str = ET.tostring(root, encoding='unicode')
            formatted_xml = etree.tostring(
                etree.fromstring(xml_str), 
                pretty_print=True, 
                encoding='unicode'
            )
            
            logger.info(f"CSV convertido para XML: {len(df)} registros")
            return True, formatted_xml
            
        except Exception as e:
            logger.error(f"Erro na conversão CSV para XML: {e}")
            return False, str(e)
    
    def _clean_column_name(self, column_name):
        """Limpa nomes de colunas para XML válido"""
        import re
        # Remover caracteres especiais e espaços
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(column_name))
        # Garantir que não começa com número
        if clean_name[0].isdigit():
            clean_name = 'col_' + clean_name
        return clean_name.lower()
    
    def generate_xsd_from_xml(self, xml_content, target_namespace="http://kaggle-data.local"):
        """Gera schema XSD a partir de XML"""
        try:
            root = ET.fromstring(xml_content)
            
            # Criar XSD básico
            xsd_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="{target_namespace}"
           xmlns="{target_namespace}"
           elementFormDefault="qualified">

    <xs:element name="{root.tag}">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="metadata" minOccurs="0">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="columns">
                                <xs:complexType>
                                    <xs:sequence>
                                        <xs:element name="column" maxOccurs="unbounded">
                                            <xs:complexType>
                                                <xs:attribute name="name" type="xs:string"/>
                                                <xs:attribute name="type" type="xs:string"/>
                                                <xs:attribute name="non_null" type="xs:string"/>
                                            </xs:complexType>
                                        </xs:element>
                                    </xs:sequence>
                                </xs:complexType>
                            </xs:element>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="data">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="record" maxOccurs="unbounded">
                                <xs:complexType>
                                    <xs:sequence>
                                        <xs:any maxOccurs="unbounded" processContents="lax"/>
                                    </xs:sequence>
                                    <xs:attribute name="id" type="xs:string"/>
                                </xs:complexType>
                            </xs:element>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
            <xs:attribute name="source" type="xs:string"/>
            <xs:attribute name="generated" type="xs:dateTime"/>
            <xs:attribute name="records" type="xs:integer"/>
        </xs:complexType>
    </xs:element>

</xs:schema>'''
            
            logger.info("XSD schema gerado com sucesso")
            return True, xsd_content
            
        except Exception as e:
            logger.error(f"Erro ao gerar XSD: {e}")
            return False, str(e)
    
    def query_xml_xpath(self, xml_content, xpath_expression):
        """Executa consulta XPath sobre XML"""
        try:
            doc = etree.fromstring(xml_content.encode('utf-8'))
            results = doc.xpath(xpath_expression)
            
            # Verificar se o resultado é um valor escalar (número, booleano, string)
            if isinstance(results, (int, float, bool, str)):
                logger.info(f"XPath query executada: resultado escalar = {results}")
                return True, {
                    'xpath': xpath_expression,
                    'results_count': 1,
                    'results': [results]
                }
            
            # Converter resultados para formato serializável
            formatted_results = []
            for result in results:
                if isinstance(result, etree._Element):
                    formatted_results.append({
                        'tag': result.tag,
                        'text': result.text,
                        'attributes': dict(result.attrib),
                        'xml': etree.tostring(result, encoding='unicode')
                    })
                else:
                    formatted_results.append(str(result))
            
            logger.info(f"XPath query executada: {len(formatted_results)} resultados")
            return True, {
                'xpath': xpath_expression,
                'results_count': len(formatted_results),
                'results': formatted_results
            }
            
        except Exception as e:
            logger.error(f"Erro na consulta XPath: {e}")
            return False, str(e)
    
    def query_xml_xquery(self, xml_content, xquery_expression):
        """Executa consulta XQuery sobre XML (simulada com XPath)"""
        try:
            xquery_to_xpath_map = {
                'count(//record)': 'count(//record)',
                'distinct-values(//*/text())': '//*[not(preceding::*[text()=current()/text()])]/text()',
                'for $r in //record return $r': '//record'
            }
            
            xpath_expr = xquery_to_xpath_map.get(xquery_expression, xquery_expression)
            
            success, result = self.query_xml_xpath(xml_content, xpath_expr)
            
            if success:
                result['original_xquery'] = xquery_expression
                result['converted_xpath'] = xpath_expr
                logger.info("XQuery convertida e executada via XPath")
            
            return success, result
            
        except Exception as e:
            logger.error(f"Erro na consulta XQuery: {e}")
            return False, str(e)
    
    def save_xml_output(self, xml_content, filename):
        """Salva XML processado na pasta de outputs"""
        try:
            os.makedirs(self.xml_outputs_path, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{timestamp}_{filename}"
            output_path = os.path.join(self.xml_outputs_path, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            logger.info(f"XML salvo em: {output_path}")
            return True, output_path
            
        except Exception as e:
            logger.error(f"Erro ao salvar XML: {e}")
            return False, str(e)