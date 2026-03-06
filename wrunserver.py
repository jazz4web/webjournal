import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'webapp:app', host='192.168.1.101',
        reload=True, port=5000, log_level='info')
