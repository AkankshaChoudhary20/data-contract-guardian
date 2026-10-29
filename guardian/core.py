import csv
import io
import json
import math

TYPES = {'string', 'integer', 'number', 'boolean'}
MAX_ROWS = 10000

def finite_number(value):
    # Python integers are unbounded; converting a valid large int to float
    # just to call isfinite can itself raise OverflowError.
    return type(value) is int or (type(value) is float and math.isfinite(value))

def check_contract(contract):
    if not isinstance(contract, dict) or not isinstance(contract.get('fields'), dict) or not contract['fields']:
        raise ValueError('Contract must contain a nonempty fields object.')
    if set(contract) - {'fields', 'allow_extra'}:
        raise ValueError('Unknown contract option.')
    if 'allow_extra' in contract and not isinstance(contract['allow_extra'], bool):
        raise ValueError('allow_extra must be boolean.')
    for name, rule in contract['fields'].items():
        if not isinstance(name, str) or not name.strip() or not isinstance(rule, dict) or not isinstance(rule.get('type'), str) or rule['type'] not in TYPES:
            raise ValueError(f'Invalid field rule: {name}')
        if set(rule) - {'type', 'required', 'nullable', 'unique', 'enum', 'min', 'max'}:
            raise ValueError(f'Unknown constraint for {name}.')
        for flag in ('required', 'nullable', 'unique'):
            if flag in rule and not isinstance(rule[flag], bool):
                raise ValueError(f'{name}.{flag} must be boolean.')
        if 'enum' in rule and (not isinstance(rule['enum'], list) or not rule['enum']):
            raise ValueError(f'{name}.enum must be a nonempty list.')
        for bound in ('min','max'):
            if bound in rule and (rule['type'] not in {'number','integer'} or not finite_number(rule[bound])):
                raise ValueError(f'{name}.{bound} must be a finite numeric constraint.')
        if 'min' in rule and 'max' in rule and rule['min'] > rule['max']:
            raise ValueError(f'{name}.min exceeds max.')
    return contract

def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON field: {key}')
        result[key] = value
    return result


def _finite_json_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError('JSON number exceeds the finite floating-point range.')
    return value


def parse_data(content, format):
    if format == 'json':
        rows = json.loads(content, parse_float=_finite_json_float, object_pairs_hook=_unique_object, parse_constant=lambda s: (_ for _ in ()).throw(ValueError(f'Invalid JSON constant: {s}')))
        if not isinstance(rows, list):
            raise ValueError('JSON data must be an array of objects.')
    elif format == 'csv':
        reader = csv.DictReader(io.StringIO(content.removeprefix('\ufeff'), newline=''), strict=True)
        try:
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames) or any(not f for f in reader.fieldnames):
                raise ValueError('CSV must have nonempty, unique column headers.')
            rows = []
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError('CSV row width differs from its header.')
                rows.append(row)
                if len(rows) > MAX_ROWS:
                    raise ValueError('Maximum dataset size is 10,000 rows.')
        except csv.Error as error:
            raise ValueError(f'Malformed CSV near line {reader.line_num}: {error}') from error
    else:
        raise ValueError('Format must be json or csv.')
    if len(rows) > MAX_ROWS or any(not isinstance(r, dict) for r in rows):
        raise ValueError('Data must contain at most 10,000 object rows.')
    return rows

def convert(value, kind, csv_mode):
    if csv_mode:
        try:
            if kind == 'integer': value = int(value)
            elif kind == 'number': value = float(value)
            elif kind == 'boolean':
                if value.lower() not in ('true','false'): return False, value
                value = value.lower() == 'true'
        except (ValueError, TypeError, AttributeError): return False, value
    valid = {'string': isinstance(value,str), 'integer': type(value) is int,
             'number': finite_number(value), 'boolean': type(value) is bool}[kind]
    return valid, value

def validate(contract, rows, csv_mode=False):
    check_contract(contract)
    if len(rows) > MAX_ROWS or any(not isinstance(r,dict) for r in rows):
        raise ValueError('Data must contain at most 10,000 object rows.')
    issues, total, bad_rows = [], 0, set()
    seen = {name: set() for name in contract['fields']}
    def issue(index, field, code, message):
        nonlocal total
        total += 1; bad_rows.add(index)
        if len(issues) < 500: issues.append({'row': index + 1, 'field': field, 'code': code, 'message': message})
    for index, row in enumerate(rows):
        if not contract.get('allow_extra', False):
            for name in sorted(set(row) - set(contract['fields'])):
                issue(index,name,'extra','Unexpected field.')
        for name, rule in contract['fields'].items():
            if name not in row:
                if rule.get('required',True): issue(index,name,'missing','Required field is missing.')
                continue
            value = row[name]
            if value is None or (csv_mode and value == ''):
                if not rule.get('nullable',False): issue(index,name,'null','Null/empty value is not allowed.')
                continue
            valid,value = convert(value,rule['type'],csv_mode)
            if not valid:
                issue(index,name,'type',f"Expected {rule['type']}."); continue
            if 'enum' in rule and not any(type(value) is type(item) and value == item for item in rule['enum']):
                issue(index,name,'enum','Value is outside the allowed set.')
            if 'min' in rule and value < rule['min']: issue(index,name,'min','Value is below minimum.')
            if 'max' in rule and value > rule['max']: issue(index,name,'max','Value exceeds maximum.')
            if rule.get('unique',False):
                # Numeric equality must agree with the number type: 1 and 1.0
                # represent the same value, including negative and positive zero.
                key = value if rule['type'] in {'number', 'integer'} else json.dumps(value,sort_keys=True)
                if key in seen[name]: issue(index,name,'duplicate','Duplicate field value.')
                seen[name].add(key)
    return {'valid': total == 0, 'rows':len(rows), 'invalid_rows':len(bad_rows), 'issue_count':total,
            'issues':issues, 'truncated':total > len(issues)}

def compare(old, new):
    check_contract(old); check_contract(new)
    changes = []
    def add(field, message, breaking): changes.append({'field':field,'message':message,'breaking':breaking})
    for field, rule in new['fields'].items():
        previous = old['fields'].get(field)
        if previous is None:
            add(field,'Field added.',rule.get('required',True)); continue
        if previous['type'] != rule['type']: add(field,'Type changed.',True)
        for key, default in [('required',True),('unique',False)]:
            if not previous.get(key,default) and rule.get(key,default): add(field,f'{key} constraint tightened.',True)
        if previous.get('nullable',False) and not rule.get('nullable',False): add(field,'Nullability tightened.',True)
        for key in ['min','max','enum']:
            # Python considers 1 == 1.0 == True; enum validation distinguishes types.
            changed = previous.get(key) != rule.get(key)
            if key == 'enum':
                changed = json.dumps(previous.get(key)) != json.dumps(rule.get(key))
            if changed:
                tightening = key in rule and (key not in previous or (key == 'min' and rule[key] > previous[key]) or (key == 'max' and rule[key] < previous[key]) or (key == 'enum' and any(not any(type(x) is type(y) and x == y for y in rule[key]) for x in previous[key])))
                add(field,f'{key} changed.',tightening)
        if previous != rule and not any(c['field'] == field for c in changes): add(field,'Constraints changed.',False)
    for field in set(old['fields']) - set(new['fields']): add(field,'Field removed.',not new.get('allow_extra',False))
    if old.get('allow_extra',False) != new.get('allow_extra',False): add('*','Extra-field policy changed.',not new.get('allow_extra',False))
    return {'breaking':any(c['breaking'] for c in changes),'changes':changes}

