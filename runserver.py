import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'webapp:app', host='127.0.0.1',
        reload=True, port=8000, log_level='info')
