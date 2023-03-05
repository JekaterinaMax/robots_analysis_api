import requests
from requests.exceptions import HTTPError
import json
import sys
import runpy

import json
import mysql.connector

import jinja2

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_contracts_by_region(region_code):
    url = f'https://bus.gov.ru/public/agency/agency.json?agency={region_code}'
    data = requests.get(url, verify=False).json()
    return data


try:
    result = get_contracts_by_region(248885)
except:  # catch *all* exceptions
    e = sys.exc_info()[0]
with open('result.json', 'w') as json_file:
    json.dump(result, json_file)


def recurs_find_key(key, obj):
    if obj == None:
        return None
    else:
        if key in obj:
            return obj[key]
        if type(obj) == dict or type(obj) == list:
            for k, v in obj.items():
                if type(v) == dict:
                    result = recurs_find_key(key, v)
                    return result
                elif type(v) == list:
                    for el in range(len(v)):
                        result = recurs_find_key(key, v[el-1])
                        return result


def get_top_docs():
    with open('result.json', 'r') as f:
        json_data = json.loads(f.read())
        top_docs = []

        data = json_data['docs']['APPOINTMENT_MEMBERS']
        cnx = mysql.connector.connect(user='dakwol', password='dakwol892',
                                      host='127.0.0.1', database='docs',
                                      auth_plugin='mysql_native_password',
                                      charset='utf8mb4',
                                      use_unicode=True)
        cursor = cnx.cursor()

        add_doc = ("INSERT INTO memDoc "
                   "(doc_name, member_name) "
                   "VALUES (%s, %s)")

        for member in data:
            doc_arr = {}

            doc_name = recurs_find_key('documentName', member)
            doc_arr['doc_name'] = doc_name

            member_name = recurs_find_key('ownerFullName', member)
            doc_arr['member_name'] = member_name

            data_doc = (doc_name, member_name)
            # Insert new employee
            cursor.execute(add_doc, data_doc)
            emp_no = cursor.lastrowid
            cnx.commit()

            top_docs.append(doc_arr)

    cursor.close()
    cnx.close()

    return top_docs


def create_message(top_docs):
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')

    table = template.render(items=top_docs)
    # менять путь на свой
    with open("C:/Users/noten/OneDrive/Desktop/task/table.html", "w", encoding="utf-8") as fh:
        fh.write(table)
    return table


create_message(get_top_docs())
