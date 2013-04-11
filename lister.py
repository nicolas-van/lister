


#parameters
number = 4
chars_number = 26

def array_to_chars(array):
    tmp = ""
    for i in array:
        tmp += chr(97 + i)
    return tmp

def chars_to_array(str):
    tmp = []
    for i in str:
        tmp.append(ord(i) - 97)
    return tmp
#end of parameters

import urllib2
import json

import sqlalchemy as sa
from pyphilo import *
import pyphilo
import os.path
from pprint import pprint

DEBUG = False

engine.init_global_engine('sqlite:///domains.db', echo=DEBUG)

class Domain(Base):
    domain = sa.Column(sa.String(50), nullable=False, unique=True, index=True)
    free = sa.Column(sa.Boolean(), nullable=False)

pyphilo.init_db()


def free_domain(domain):
    stream = urllib2.urlopen("http://domai.nr/api/json/info?q=" + domain + ".com")
    try:
        content = json.loads(stream.read())
    finally:
        stream.close()

    if content["availability"] == "available":
        return True
    else:
        return False

def add_one(chars):
    i = len(chars) - 1
    while i >= 0:
        chars[i] = (chars[i] + 1) % chars_number
        if chars[i] != 0:
            break
        i -= 1
    return chars

if __name__ == "__main__":
    chars = [0 for x in range(number)]
    final = [chars_number - 1 for x in range(number)]

    @transactionnal
    def get_last():
        last = session.query(Domain).order_by(Domain.domain.desc()).limit(1).all()
        if len(last) > 0:
            return last[0].domain
        return None

    last_domain = get_last()
    if last_domain:
        chars = chars_to_array(last_domain)
        chars = add_one(chars)

    while True:
        domain = array_to_chars(chars)
        result = free_domain(domain)

        @transactionnal
        def add_data():
            d = Domain(domain=domain, free=result)
            session.add(d)
        add_data()

        print "%s : %s" % (domain, "free" if result else "taken")

        if chars == final:
            break

        chars = add_one(chars)

