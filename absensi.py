from os import stat
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib3 import exceptions
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import json

# for explicity wait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys 

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r"C:\Users\Lenovo\AppData\Local\Google\Chrome\Application\chrome.exe"
chrome_options.add_experimental_option('detach',True)

chrome = webdriver.Chrome(options=chrome_options,service=Service(ChromeDriverManager().install()))
chrome.implicitly_wait(10)

DATA = json.load(open('./info.json'))
FIELDS = json.load(open('./fields.json')) 
url = DATA['link']


def load_page():
    chrome.get(url)
    chrome.maximize_window()

## BUG
# def new_tab():
#     body = chrome.find_element(By.TAG_NAME,'body')
#     print(body)
#     if body:
#         body.send_keys(Keys.CONTROL + 't')
#     sleep(.5)

def status(m):
    print(f"[STATUS]: {m}")

def error(m):
    print(f"[ERROR]: {m}")

def debug(m):
    print(f"[DEBUG]: {m}")

def target(selector):
    return chrome.find_element(By.XPATH, selector)

def move_page():
    target(FIELDS['next']).click()
    WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((
        By.XPATH, FIELDS['next']
    ))).click()
    sleep(1)


def kirim():
    WebDriverWait(chrome,5).until(EC.element_to_be_clickable((
        By.XPATH,FIELDS['kirim'])
    )).click()


def choice_action(name,pertemuan=False,minggu=False):

    try:
        WebDriverWait(chrome,10).until(EC.element_to_be_clickable((
            By.XPATH, FIELDS['choices'][name][0]
        ))).click()
       
       
        value = ''
        if name == 'pertemuan': 
            print(name,pertemuan)
            value = FIELDS['choices'][name][1].replace(f'#{name.upper()}',str(pertemuan))
        elif name == 'minggu':
            print(name,minggu)
            value = FIELDS['choices'][name][1].replace(f'#{name.upper()}',str(minggu))
        else: 
            value = FIELDS['choices'][name][1].replace(f'#{name.upper()}',DATA[name])

        waiter = WebDriverWait(chrome,10).until(
            EC.element_to_be_clickable((By.XPATH, value))
        )
        waiter.click()
        status(f'{name} sudah berhasil di input')
    except:
        error(f'field {name} gagal di input')
    finally:
        sleep(.5)


def radio_action(name):
    value = FIELDS['radio'][name].replace(f'#{name.upper()}',DATA[name]) 
    try:
        WebDriverWait(chrome,10).until(
            EC.element_to_be_clickable((By.XPATH, value))
        ).click()
    except:
        error(f'field {name} gagal di input')
    finally:
        sleep(.5)

def text_action(name,identitas_mhs=False):

    order = ['nama','nim','noHP']
    some_shit = False 

    if identitas_mhs:
        try:
            WebDriverWait(chrome, .5).until(EC.visibility_of_element_located((
                By.XPATH, "//div[contains(text(),'Identitas Mahasiswa')]"
            )))
            some_shit = True
        except:
            pass

    try:

        pointer = FIELDS['text'][name]

        if identitas_mhs:
            pointer = pointer.replace(f'#{name.upper()}_POS',str((order.index(name) + 1) + int(some_shit)))


        WebDriverWait(chrome,10).until(
            EC.presence_of_element_located((By.XPATH, pointer))
        ).send_keys(DATA[name])
        status(f'field {name} sudah berhasil di input')
    except:
        error(f'field {name} gagal di input')
    finally:
        sleep(1)




def main(pertemuan,minggu):

    load_page()

### PAGE 1
    sleep(1)

## cek for dummy page 
    try:
        WebDriverWait(chrome,1).until(EC.presence_of_element_located((
            By.XPATH, FIELDS['nama']
        )))
    except:
        move_page()
        sleep(1)
            


    for field in ['nama','nim','noHP']:
        text_action(field, identitas_mhs=True)

    move_page()


### PAGE 2
    sleep(1)

    choice_action('jenjang')
    radio_action('fakultas')


    move_page()


### PAGE 3
    sleep(1)
    choice_action('program_studi')

    move_page()

### PAGE 4
    sleep(1)
    choice_action('huruf_awal_dosen')
    move_page()


### PAGE 5
    sleep(1)
    choice_action('nama_dosen')

    move_page()

### PAGE 6
    sleep(1)
    text_action('nama_dosen_1')

    move_page()

### PAGE 7 (FINAL)
    sleep(1)
    text_action('kode_mata_kuliah')
    text_action('nama_mata_kuliah')
    choice_action('jumlah_sks')
    choice_action('minggu',minggu=minggu)
    choice_action('pertemuan',pertemuan=pertemuan)

    # mengirim formulir 
    kirim()

    status('DONE')
    chrome.get_screenshot_as_file(f'./image/pertemuan{pertemuan}.png')


begin,end = map(int,DATA['pertemuan'].split('-'))
pertemuan = list(range(begin,end + 1))

begin,end = map(int,DATA['minggu'].split('-'))
minggu = list(range(begin,end + 1)) 

print(pertemuan,minggu)

if __name__ == '__main__':

    for i in range(len(pertemuan)):
        try:
            debug([pertemuan[i],minggu[i]])
            main(pertemuan=pertemuan[i],minggu=minggu[i]) 
            sleep(1)
        except: 
            error(f'pertemuan {pertemuan[i]} gagal untuk di input !!!')
            chrome.close()
            break

        status(f'pertemuan {pertemuan[i]} berhasil di input')
    else:
         chrome.close()




