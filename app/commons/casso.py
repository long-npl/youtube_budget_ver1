import os
from app.commons.crypt import encrypt, decrypt, json


def casso_path():
    path = os.getenv('LOCALAPPDATA', fr"C:\Users\{os.getlogin()}\AppData\Local")
    ck_path = os.path.join(path, "Navigator")
    os.makedirs(ck_path, exist_ok=True)

    return ck_path


def save_casso():
    login = os.getlogin()
    password = input(f"Please enter your password\nCASSO_ID: {login}\nCASSO_PW: ")

    casso = {'CASSO_ID': login,
             'CASSO_PW': password}

    file = os.path.join(casso_path(), login)
    if os.path.exists(file):
        os.unlink(file)

    with open(file, "wb") as f:
        f.write(encrypt(json.dumps(casso).encode("UTF-16")))


def load_casso():
    try:
        file = os.path.join(casso_path(), os.getlogin())
        if os.path.exists(file):
            with open(file, "rb") as f:
                bts = f.read()

            return json.loads(decrypt(bts).decode("UTF-16"))
    except:
        pass

    return {}
