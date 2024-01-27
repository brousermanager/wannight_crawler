#   OUTPUT PATH
def getOutputPathAthena(category: str, city: str) -> str:
    return 'output/outputATHENA/' + category.split('.')[0] + '-' + city.split('.')[0] + '.csv'


def getOutputPathAthenaByName(name: str) -> str:
    return 'output/outputATHENA/' + name + '.csv'


def getOutputPathApollo(str: str) -> str:
    return 'output/outputAPOLLO/' + str + '.csv'


def getOutputPathDioniso(str: str) -> str:
    return 'output/outputDIONISO/' + str + '.json'


#   INPUT PATH
def getCategoryPath(category: str) -> str:
    return 'input/categoryFiles/' + category + '.txt'


def getCityPath(city: str) -> str:
    return 'input/cityFiles/' + city + '.txt'


def getSettingsPath(settings: str) -> str:
    return 'input/settingsFiles/' + settings + '.txt'
