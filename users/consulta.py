import base64
import os
import re
import time
from PyPDF2 import PdfReader, PdfWriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from config import CONVENIO, USERNAME, PASSWORD
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


def remove_html_from_pdf(html, output_file):
    soup = BeautifulSoup(html, "html.parser")
    for tbody in soup.find_all("tbody"):
        if "Código do Convênio" in tbody.get_text() and "Identificação do Operador" in tbody.get_text():
            tbody.decompose()
    return str(soup)


def remove_phrases_from_pdf(pdf_file, output_file):
    phrases_to_remove = [
        "Código do Convênio 00075161-8",
        "Identificação do Operador FLAVIO"
    ]

    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()

        for phrase in phrases_to_remove:
            text = re.sub(re.escape(phrase), '', text)

        pdf_writer.add_page(page)

    with open(output_file, 'wb') as out:
        pdf_writer.write(out)


def login(browser):
    time.sleep(2)
    browser.get('https://caixaaqui.caixa.gov.br/caixaaqui/CaixaAquiController')
    time.sleep(2)
    convenio_input = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#convenio')))
    convenio_input.send_keys(CONVENIO)
    
    login_input = browser.find_element(By.CSS_SELECTOR, '#login')
    login_input.send_keys(USERNAME)
    
    password_input = browser.find_element(By.CSS_SELECTOR, '#password')
    password_input.send_keys(PASSWORD)
    
    submit_button = browser.find_element(By.CSS_SELECTOR, '.btn-azul')
    submit_button.click()
    time.sleep(5)
    
def handle_alert_and_login(browser):
    try:
        alert = browser.switch_to.alert
        alert_text = alert.text
        print(f"Alert Text: {alert_text}")
        alert.accept()  # Aceitar o alerta
        print("Realizando login novamente...")
        login(browser)
    except:
        print("Não foi possível lidar com o alerta ou nenhum alerta encontrado.")


def consulta_cpf_func(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)

    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })

    browser = webdriver.Chrome(options=chrome_options)

    try:
        login(browser)

        try:
            time.sleep(2)
            submit_button_sim = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-azul")))
            submit_button_sim.click() 
            # Depois de enviar o CPF, envie a tecla "Enter"
            cpf_input.send_keys(Keys.ENTER)  
                 
        except:
            handle_alert_and_login(browser)
        
        
        browser.get('https://caixaaqui.caixa.gov.br/caixaaqui/CaixaAquiController/resumo_cliente/resumo_cliente_init')

        cpf_input = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/center/div[2]/div[2]/form/center/table/tbody/tr[2]/td/input')))
        cpf_input.send_keys(cpf)
        time.sleep(2)

        submit_button_cpf = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/center/div[2]/div[2]/form/center/table/tbody/tr[2]/td/a')))
        submit_button_cpf.click()
        time.sleep(3)

        directory = 'static/uploads/PDF'

        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = os.path.join(directory, f"{cpf}.pdf")

        pdf_content = browser.execute_cdp_cmd("Page.printToPDF", {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
        })

        with open(filename, 'wb') as f:
            f.write(base64.b64decode(pdf_content['data']))

        output_filename = os.path.join(directory, f"{cpf}.pdf")

        html_content = browser.execute_script("return document.documentElement.outerHTML")
        modified_html = remove_html_from_pdf(html_content, output_filename)
        
        with open(output_filename, 'wb') as f:
            f.write(base64.b64decode(pdf_content['data']))

        remove_phrases_from_pdf(output_filename, output_filename)

        file_url = f"static/uploads/PDF/{cpf}_modified.pdf"
        return {"message": "Consulta concluída com sucesso.", "file_url": file_url}

    except Exception as e:
        print(f"Exception encountered: {e}")

    finally:
        browser.quit()
