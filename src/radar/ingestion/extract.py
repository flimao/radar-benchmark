"""Explicit selectors; ambiguous/missing values stop extraction instead of guessing."""
import csv
import io
import json
import re
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path


def number(value, locale='en', *, dash_zero=False):
    if value is None or isinstance(value, bool):
        raise ValueError('Valor numérico ausente/inválido.')
    if isinstance(value, str):
        value = value.strip().replace('\u00a0', '').replace(' ', '').replace('−', '-')
        if value in ('-', '—', '–'):
            if dash_zero:
                return Decimal(0)
            raise ValueError('Traço não foi explicitamente mapeado como zero.')
        negative = value.startswith('(') and value.endswith(')')
        if negative:
            value = value[1:-1]
        if locale == 'pt':
            value = value.replace('.', '').replace(',', '.')
        elif locale == 'en':
            value = value.replace(',', '')
        else:
            raise ValueError('Locale deve ser en ou pt.')
        if negative:
            value = '-' + value
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Valor não numérico.') from exc
    if not result.is_finite():
        raise ValueError('Valor não finito.')
    return result


def extract(path, kind, selector):
    path = Path(path)
    if kind == 'xlsx':
        from openpyxl import load_workbook
        with zipfile.ZipFile(path) as archive:
            if sum(p.file_size for p in archive.infolist()) > 100*1024*1024:
                raise ValueError('XLSX descompactado excede 100 MB.')
        with path.open('rb') as handle:
            book = load_workbook(handle, read_only=True, data_only=True)
            try:
                sheet = book[selector['sheet']]
                for guard in selector.get('guards', []):
                    if str(sheet[guard['cell']].value).strip() != str(guard['equals']).strip():
                        raise ValueError('Cabeçalho/rótulo XLSX mudou; revise o mapeamento.')
                value = sheet[selector['cell']].value
                if value is None:
                    raise ValueError('Célula vazia ou fórmula sem valor calculado no arquivo.')
                return value, f"{selector['sheet']}!{selector['cell']}"
            finally:
                book.close()
    if kind == 'pdf':
        import pymupdf
        with pymupdf.open(path) as document:
            page_number = int(selector['page'])
            if page_number < 1 or page_number > len(document):
                raise ValueError('Página PDF fora do documento.')
            text = document[page_number-1].get_text()
            for expected in selector.get('guards', []):
                if expected not in text:
                    raise ValueError('Cabeçalho PDF mudou; revise o mapeamento.')
            # Use an exact line and a specified following column. Repeated labels
            # require an explicit occurrence (e.g. dividends vs share issuances).
            lines = [line.strip() for line in text.splitlines()]
            positions = [i for i,line in enumerate(lines) if line == selector['label']]
            if not positions:
                raise ValueError('Rótulo não encontrado no PDF (OCR não habilitado).')
            if len(positions) > 1 and 'occurrence' not in selector:
                raise ValueError('Rótulo PDF ambíguo; informe occurrence.')
            occurrence = int(selector.get('occurrence', 0))
            index = positions[occurrence] + int(selector.get('offset',1)) + int(selector.get('column', 0))
            if index < 0 or index >= len(lines):
                raise ValueError('Posição PDF fora das linhas da página.')
            value = lines[index]
            return value, f"p.{page_number}; {selector['label']}; coluna {int(selector.get('column',0))+1}; ocorrência {occurrence+1}"
    if kind == 'html':
        from html.parser import HTMLParser
        class TextParser(HTMLParser):
            def __init__(self):
                super().__init__(); self.parts=[]
            def handle_data(self, value):
                self.parts.append(value)
        parser=TextParser(); parser.feed(path.read_text(encoding='utf-8'))
        text=' '.join(' '.join(parser.parts).split())
        if not selector.get('guards') or any(g not in text for g in selector['guards']):
            raise ValueError('Contexto HTML mudou; revise o mapeamento.')
        matches=list(re.finditer(selector['pattern'],text))
        if selector.get('allow_identical_duplicates') and matches and len({m.group(1) for m in matches})==1:
            matches=matches[:1]
        if len(matches)!=1:
            raise ValueError('Seletor HTML ausente/ambíguo.')
        return matches[0].group(1), 'HTML; '+selector['pattern']
    if kind == 'csv':
        rows = list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig')),
                                   delimiter=selector.get('delimiter', ',')))
        matches = [r for r in rows if all(r.get(k) == str(v) for k,v in selector['where'].items())]
        if len(matches) != 1:
            raise ValueError('Seletor CSV exige exatamente uma linha.')
        return matches[0][selector['column']], f"CSV {selector['where']}; coluna {selector['column']}"
    if kind == 'json':
        value = json.loads(path.read_text(), parse_float=Decimal)
        for guard in selector.get('guards',[]):
            actual=value
            for key in guard['path']:actual=actual[key]
            if str(actual)!=str(guard['equals']):
                raise ValueError('Identidade/cabeçalho JSON diverge do mapeamento.')
        if selector.get('taxonomy'):
            facts=value['facts'][selector['taxonomy']][selector['tag']]['units'][selector['unit']]
            selected=[v for v in facts if all(v.get(k)==expected for k,expected in selector['where'].items())]
            if len(selected)!=1:
                raise ValueError('XBRL exige exatamente um fato: selecione datas, formulário e accession sem ambiguidade.')
            fact=selected[0]
            return fact['val'], 'XBRL '+selector['taxonomy']+':'+selector['tag']+'; '+selector['unit']+'; '+json.dumps(selector['where'])+'; accession '+fact['accn']
        for key in selector['path']:
            value = value[key]
        if isinstance(value, (dict, list)):
            raise ValueError('Seletor JSON não aponta para um valor escalar.')
        return value, 'JSON ' + json.dumps(selector['path'])
    raise ValueError('Formato suportado: xlsx, pdf, csv, json.')
