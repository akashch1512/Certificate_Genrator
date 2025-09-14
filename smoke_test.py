from Tools.image_overlay import generate_certificate
import os
user={'id':'40001','fname':'Akash','lname':'Chaudhari','year':'3'}
template_dir=os.path.join('data','certificate')
template=None
if os.path.isdir(template_dir):
    for f in os.listdir(template_dir):
        if f.lower().endswith(('.png','.jpg','.jpeg')):
            template=os.path.join(template_dir,f)
            break

out='data/generated/test_cert.png'
if not template:
    print('NO_TEMPLATE')
else:
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p=generate_certificate(template,out,user,signs_dir=os.path.join('data','signs'))
    print('SAVED',p)
