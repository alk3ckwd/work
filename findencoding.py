import libmagic as magic
blob=open('Metro Peds Patient Panel Discrete Pat Name Fields_07242016.csv')
m = magic.Magic(mime_encoding=True)
encoding = m.from_buffer(blob)
