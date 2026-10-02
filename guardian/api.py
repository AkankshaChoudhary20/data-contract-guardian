import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .core import check_contract,parse_data,validate,compare
from . import store

app=FastAPI(title='Data Contract Guardian')
DB=os.getenv('GUARDIAN_DB','data/guardian.sqlite')
STATIC=Path(__file__).resolve().parent.parent/'static'

async def body(request):
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>2_000_000: raise HTTPException(413,'Maximum request size is 2 MB.')
    import json
    try:
        data=json.loads(raw)
        if not isinstance(data,dict): raise ValueError()
        return data
    except ValueError: raise HTTPException(400,'Invalid JSON request.')

@app.exception_handler(ValueError)
async def value_error(request,error):
    from fastapi.responses import JSONResponse
    return JSONResponse({'detail':str(error)},status_code=400)

@app.get('/api/contracts')
def contracts(): return store.list_all(DB)

@app.post('/api/contracts')
async def create(request:Request):
    data=await body(request)
    name=data.get('name','')
    if not isinstance(name,str) or not 1<=len(name.strip())<=100: raise ValueError('Contract name must be 1–100 characters.')
    schema=check_contract(data.get('schema'))
    return store.save(DB,name.strip(),schema)

@app.post('/api/validate')
async def run(request:Request):
    data=await body(request)
    saved=store.get(DB,data.get('contract_id'))
    if not saved: raise HTTPException(404,'Contract not found.')
    content=data.get('content')
    if not isinstance(content,str): raise ValueError('Dataset content must be text.')
    format=data.get('format','json')
    return validate(saved['schema'],parse_data(content,format),format=='csv')

@app.post('/api/compare')
async def diff(request:Request):
    data=await body(request)
    old=store.get(DB,data.get('old_id'));new=store.get(DB,data.get('new_id'))
    if not old or not new: raise HTTPException(404,'Select two saved contracts.')
    return compare(old['schema'],new['schema'])

@app.get('/')
def index(): return FileResponse(STATIC/'index.html')
app.mount('/static',StaticFiles(directory=STATIC),name='static')
