import re
import pandas as pd

used_cols = ['name', 'address', 'product', 'quantity', 'order_no']
df = pd.DataFrame(columns=used_cols)

# def extract_shopee_with_image(doc, page_num):
#     name_address = []
#     page = doc[page_num]
#     image_list = page.get_images()
#     for idx, img in enumerate(image_list, start=1):
#         if idx in [3,5]:
#             data = doc.extract_image(img[0])
#             image_stream = data.get('image')
#             reader = easyocr.Reader(['th','en'], gpu=True)
#             result = reader.readtext(image_stream)
#             text = [item[1] for item in result]
#             name_address.append("".join(text))
#     prd_chk, ord_chk = 0,0
#     prd, prd_tmp , qty, ord_no = [],'',[],''
#     words = page.get_text('dict')
#     for b in words["blocks"]:
#         if b['type'] == 1:
#             continue
#         else:
#             for l in b['lines']:
#                 for s in l['spans']:
#                     if s['text'].startswith('Shopee Order No'):
#                         ord_chk = 1
#                     elif ord_chk == 1:
#                         ord_no = s['text']
#                         ord_chk = 0
#                     elif s['text'] == 'Qty':
#                         prd_chk = 1
#                     elif prd_chk == 1 and not s['text'].isdigit():
#                         prd_chk = 0
#                     elif prd_chk == 1 and s['text'].isdigit():
#                         prd_chk = 2
#                     elif prd_chk == 2:
#                         if prd_tmp == 'Total:':
#                             prd_tmp = ''
#                             prd_chk = 0 
#                         elif s['text'].isdigit():
#                             prd.append(prd_tmp)
#                             qty.append(int(s['text']))
#                             prd_tmp = ''
#                             prd_chk = 1
#                         else:
#                             prd_tmp += s['text'].strip()

#     new_rows = [['','',prd[i],qty[i],''] for i in range(len(prd))]
#     temp = pd.DataFrame(new_rows, columns=used_cols)
#     temp['name'] = name_address[0]
#     temp['address'] = name_address[1]
#     temp['order_no'] = ord_no
#     temp['post_code'] = temp['address'].apply(lambda x: re.findall(r"\d{5}", x)[0] if len(re.findall(r"\d{5}", x)) > 0 else '')
    
#     return temp

def extract_shopee(doc, page_num):
    words = doc[page_num].get_text('dict')
    prd_chk, adr_chk, name_chk = 0,1,0
    prd, prd_tmp , qty, ord_no, adr, post_code, name = [],'',[],'','','',''
    for b in words["blocks"]:
        if b['type'] == 1:
            continue
        else:
            for l in b['lines']:
                for s in l['spans']:
                    if s['text'].startswith('Shopee Order No') and len(s['text']) > 16:
                        ord_no = s['text'].strip()[17:]
                    elif s['text'] == 'Qty':
                        prd_chk = 1
                    elif prd_chk == 1 and not s['text'].isdigit():
                        prd_chk = 0
                    elif prd_chk == 1 and s['text'].isdigit():
                        prd_chk = 2
                    elif prd_chk == 2:
                        if prd_tmp == 'Total:':
                            prd_tmp = ''
                            prd_chk = 0 
                        elif s['text'].isdigit():
                            prd.append(prd_tmp)
                            qty.append(int(s['text']))
                            prd_tmp = ''
                            prd_chk = 1
                        else:
                            prd_tmp += s['text'].strip()
                    elif s['text'][:7] == 'จังหวัด' and adr_chk == 1 and len(s['text']) > 7:
                        adr += s['text'][7:]
                        adr_chk += 1
                    elif adr_chk == 2:
                        adr_chk = 0
                        post_code = s['text'].strip()[:5]
                    elif s['text'] == ' (FROM)':
                        name_chk += 1
                    elif s['text'].strip() == 'เลขที่':
                        name_chk = 0
                    elif name_chk == 1:
                        name += s['text']
    new_rows = [['','',prd[i],qty[i],''] for i in range(len(prd))]
    temp = pd.DataFrame(new_rows, columns=used_cols)
    temp['name'] = name
    temp['address'] = adr
    temp['order_no'] = ord_no
    temp['post_code'] = post_code
    
    return temp

def extract_tiktok(doc, page_num):
    words = doc[page_num].get_text('dict')
    adr_chk, name_chk, ord_chk, prd_chk = 1,0,0,0
    adr, name, ord_no, prd, prd_tmp , qty = '','','',[],'',[]
    for b in words["blocks"]:
        if b['type'] == 1:
            continue
        else:
            for l in b['lines']:
                for s in l['spans']:
                    if 'ชําระโดย' in s['text']:
                        adr_chk = 0
                    elif adr_chk == 1:
                        adr += s['text']
                    elif s['text'] == 'ถึง':
                        name_chk = 1
                    elif name_chk == 1:
                        name = s['text']
                        name_chk = 0
                    elif s['text'] == 'Order ID':
                        ord_chk = 1
                    elif ord_chk == 1:
                        ord_no = s['text']
                        ord_chk = 0
                    elif s['text'] == 'Qty':
                        prd_chk = 1
                    elif prd_chk == 1 and not s['text'].isdigit():
                        prd_chk = 0
                    elif prd_chk == 1 and s['text'].isdigit():
                        prd_chk = 2
                    elif prd_chk == 2:
                        if prd_tmp == 'Total:':
                            prd_tmp = ''
                            prd_chk = 0 
                        elif s['text'].isdigit() and int(s['text']) < 20:
                            prd.append(prd_tmp)
                            qty.append(int(s['text']))
                            prd_tmp = ''
                            prd_chk = 1
                        else:
                            prd_tmp += s['text'].strip()
    new_rows = [['','',prd[i],qty[i],''] for i in range(len(prd))]
    temp = pd.DataFrame(new_rows, columns=used_cols)
    temp['name'] = name
    temp['address'] = adr
    temp['order_no'] = ord_no
    temp['post_code'] = temp['address'].apply(lambda x: re.findall(r"\d{5}", x)[0] if len(re.findall(r"\d{5}", x)) > 0 else '')
    
    return temp

def extract_lazada(doc, page_name):
    words = doc[page_name].get_text('dict')
    prd_chk, adr_chk, name_chk = 0,0,0
    prd, prd_tmp , qty, ord_no, name, adr, post_code  = [],'',[],'', '', '', ''
    for b in words["blocks"]:
        if b['type'] == 1:
            continue
        else:
            for l in b['lines']:
                for s in l['spans']:
                    if s['text'].startswith('LAZADA Order Number:'):
                        ord_no += s['text'][21:]
                    elif s['text'] == 'Qty':
                        prd_chk = 1
                    elif prd_chk == 1 and not s['text'].isdigit():
                        prd_chk = 0
                    elif prd_chk == 1 and s['text'].isdigit():
                        prd_chk = 2
                    elif prd_chk == 2:
                        if prd_tmp == 'Total:':
                            prd_tmp = ''
                            prd_chk = 0 
                        elif s['text'].isdigit():
                            prd.append(prd_tmp)
                            qty.append(int(s['text']))
                            prd_tmp = ''
                            prd_chk = 1
                        else:
                            prd_tmp += s['text'].strip()
                    elif re.match(r"\d{5}", s['text']):
                        post_code += s['text']
                    elif name_chk == 1:
                        name_chk = 0
                        name += s['text']
                    elif s['text'][:6] == '(HOME)':
                        adr_chk = 0
                    elif adr_chk == 1:
                        adr += s['text']
                    elif s['text'] == 'เพลินแล็บส์':
                        name_chk += 1
                    elif s['text'] == 'Phone:':
                        adr_chk += 1
    new_rows = [['','',prd[i],qty[i],''] for i in range(len(prd))]
    temp = pd.DataFrame(new_rows, columns=used_cols)
    temp['name'] = name
    temp['address'] = adr.split(', ')[-2].split('/ ')[0]
    temp['order_no'] = ord_no
    temp['post_code'] = post_code
    
    return temp