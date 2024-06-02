"""
WARNING:

Please make sure you install the bot with `pip install -e .` in order to get all the dependencies
on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the bot.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at https://documentation.botcity.dev/
"""


# Import for the Web Bot
from botcity.web import WebBot, Browser, By
# Import for integration with BotCity Maestro SDK
from botcity.maestro import *
# Importa a dependencia do ChromeDriverManager do webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager
# Importa a dependencia do element_as_select do botcity
from botcity.web.util import element_as_select
# Importa a dependencia do element_as_select do botcity
from botcity.web.parsers import table_to_dict
# Importa a dependencia do botcity.plugins.excel
from botcity.plugins.excel import BotExcelPlugin

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

excel = BotExcelPlugin()
excel.add_row(['NOME DA CIDADE', 'NÚMERO DE HABITANTES'])


def main():
    # Instancia do Orquestrador
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    # Instancia do bot
    bot = WebBot()

    # Configura o modo headless para False
    bot.headless = False

    # Define o navegador a ser utilizado
    bot.browser = Browser.CHROME

    # Baixa e instala a versão mais recente do ChromeDriver
    bot.driver_path = ChromeDriverManager().install()

    # Pode optar por baixar, colocar o arquivo na pasta do projeto e colocar o path para o arquivo
    # bot.driver_path = "<path to your WebDriver binary>"

    # Opens the BotCity website.
    bot.browse("https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php")

    # Localiza o dropbox UF e seleciona
    drop_uf = element_as_select(bot.find_element('//*[@id="uf"]', By.XPATH))
    drop_uf.select_by_value('RN')

    # Localiza e clica no botão pesquisar
    btn_pesquisar = bot.find_element('//*[@id="btn_pesquisar"]', By.XPATH)
    btn_pesquisar.click()

    bot.wait(1000)

    # Localiza a tabela com os dados e transforma os dados em um dicionário
    data_table = bot.find_element('//*[@id="resultado-DNEC"]', By.XPATH)
    data = table_to_dict(data_table)

    bot.wait(1000)

    next_page = bot.find_element('//*[@id="navegacao-resultado"]/a[2]', By.XPATH)
    next_page.click()

    bot.wait(1000)

    data_table_2 = bot.find_element('//*[@id="resultado-DNEC"]', By.XPATH)
    data_2 = table_to_dict(data_table_2)

    data.extend(data_2)

    bot.wait(1000)

    next_page = bot.find_element('//*[@id="navegacao-resultado"]/a[2]', By.XPATH)
    next_page.click()

    bot.wait(1000)

    data_table_3 = bot.find_element('//*[@id="resultado-DNEC"]', By.XPATH)
    data_3 = table_to_dict(data_table_3)

    data.extend(data_3)

    bot.wait(1000)

    next_page = bot.find_element('//*[@id="navegacao-resultado"]/a[2]', By.XPATH)
    next_page.click()

    bot.wait(1000)

    data_table_4 = bot.find_element('//*[@id="resultado-DNEC"]', By.XPATH)
    data_4 = table_to_dict(data_table_4)

    data.extend(data_4)

    print(data)
    # input()

    # Navega para o site do IBGE
    bot.navigate_to('https://cidades.ibge.gov.br/brasil/panorama')

    # Define uma variável string vazia
    str_previous_city = ''

    # Localiza o campo pesquisa e clica nele
    for item in data:
        # Atribui a variável str_city o valor do campo localidade da tabela
        str_city = item['localidade']

        if str_city == 'Arez':
            str_city = 'Arês'

        if str_city == 'Boa Saúde':
            str_city = 'Januário Cicco'

        if str_city == "Lagoa D'Anta":
            str_city = "Lagoa d'Anta"

        if str_city == "Olho-D'Água do Borges":
            str_city = "Olho d'Água do Borges"

        if str_city == "São Bento do Trairi":
            str_city = "São Bento do Trairí"

        # Se a variável str_previous_city for igual a variável str_city,
        # não executa as linhas abaixo, passando para o próximo item no loop
        if str_previous_city == str_city:
            continue

        if str_city == 'Lajes Pintadas':
            continue

        if str_city == 'Serrinha dos Pintos':
            continue

        if str_city == 'Tibau do Sul':
            continue

        # Localiza o campo de pesquisa
        input_pesquisar = bot.find_element('/html/body/app/shell/header/busca/div/input', By.XPATH)
        # Insere o valor da str_city no campo de pesquisa
        input_pesquisar.send_keys(str_city)

        # Localiza a tag "a" se ela contiver uma tag "span" e dentro dela o valor for igual ao da varíaval str_city
        span_pesquisa = bot.find_element(
            f'//a[span[contains(text(), "{str_city}")] and span[contains(text(), "RN")]]', By.XPATH)

        # Clica na tag "a"
        span_pesquisa.click()

        # espera 1 segundo
        bot.wait(500)

        population = bot.find_element("//div[@class='indicador__valor']", By.XPATH)

        str_population = population.text.split(' ')[0]

        # Adiciona o nome da cidade e sua população numa linha do excel
        excel.add_row([str_city, str_population])

        # Atribui à variável str_previous_city o valor da variável str_city
        str_previous_city = str_city

        # volta para o loop

    excel.write(r'C:\Desenvolvimento\_projeto_python\automacao_ibge\Cidades_RN.xlsx')

    # Wait 3 seconds before closing
    bot.wait(3000)
    # input()

    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    # bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    # maestro.finish_task(
    #     task_id=execution.task_id,
    #     status=AutomationTaskFinishStatus.SUCCESS,
    #     message="Task Finished OK."
    # )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
