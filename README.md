# Finance tracker application – kursinio darbo ataskaita

### Įžanga:

***Kas tai per programa?***
 
  Finance tracker application (liet. Finansų sekimo programa) – tai programa skirta padėti vartotojams sekti asmenines ir grupines išlaidas. Vartotojai gali nustatyti savo išlaidų limitus, pridėti išlaidas ir       stebėti ar limitai nėra viršijami. Programa palaiko kelis vartotojus, o visa informacija išsaugoma CSV failuose.

***Kaip paleisti programą?***

1.	Reikia turėti įdiegtą Python 3.11 arba naujesnę versiją
2.	Terminale įvesti:
   
        python .\finance_tracker.py
arba paspausti paleidimo mygtuką.

***Kaip naudotis programa?***

Pasirinkti vieną iš duotų keturių parinkčių: 

    Available options:
    1. Add an expense
    2. Change spending limit
    3. Add a new user
    4. Exit
    Choose an option (1, 2, 3, 4):
ir vykdyti nurodymus įrašant informaciją apie išlaidas ir vartotojus. 
Duomenys automatiškai išsaugomi users.cvs ir expenses.cvs.


### Turinys/Analizė:
***Funkciniai reikalavimai ir OOP principai:***

**Inkapsuliacija** (encapsulation) – slepia vidinius duomenis ir leidžia prieiti prie jų tik per metodus:

    class User:
        def __init__(self, name: str, limit: float):
            self.name = name
            self.limit = limit
            self.expenses = []
Vartotojo atributai, tokie kaip limitas ir išlaidos, yra valdomi per metodus, pvz., add_expense(), užtikrinant saugią prieigą prie duomenų.

**Paveldėjimas** (inheritance) – leidžia perimti savybes ir metodus iš motininės klasės:

    class GroupExpense(Expense):
        def __init__(self, amount, description, users):
            super().__init__(amount, description)
GroupExpense paveldi iš Expense, pakartotinai panaudoja bendrą logiką ir išplečia funkcionalumą grupinėms išlaidoms.

**Polimorfizmas** (polymorphism) – Tas pats metodas skirtingose klasėse gali būti realizuotas skirtingai:

    def get_details(self):
        return f"{self.description} - €{self.amount}"
Tiek Expense, tiek GroupExpense apibrėžia get_details() savaip, leidžiant polimorfiškai išvardyti išlaidas.

**Abstrakcija** (abstraction) – suteikia bendrą sąsają ir paslepia sudėtingą vidinį įgyvendinimą:

    class AbstractExpenseFactory(ABC):
        @abstractmethod
        def create_expense(self, ...): pass
Abstrakčios klasės apibrėžia išlaidų kūrimo planą, o konkretūs „factory“ klasės įgyvendina specifiką.

***Dizaino šablonai:***

Naudoti **Factory Method** ir **Abstract Factory** sukurti skirtingų tipų išlaidoms:

    class ExpenseFactory(AbstractExpenseFactory):
        def create_expense(self, expense_type, amount, description, users=None):
            ...
Šie dizaino šablonai leidžia lengvai išplėsti programą, pridedant naujus išlaidų tipus.

***Kompozicija (composition):***

FinanceTracker klasėje naudojama kompozicija su User ir Expense:

    class FinanceTracker:
        def __init__(self, users):
            self.users = users
            self.expenses = []
Vartotojai ir išlaidos sudaro FinanceTracker; vartotojai patys turi savo išlaidų sąrašus.

***Skaitymas/įrašymas į failus:***

Programa išsaugo duomenis naudodama CSV failus:

    with open('users.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        
***Testavimas:***

Naudota standartinė Python testavimo biblioteka unittest.
Testavimą paleisti galima į terminalą įrašius:

    python -m unittest .\finance_tracker.py
    
Arba testavimas automatiškai pasileidžia programai pasibaigus.
Gautas rezultatas patvirtina programos teisingumą:

    Ran 4 tests in 0.001s  
    OK
    
### Rezultatai ir išvados:
***Rezultatai:***

Vartotojai gali valdyti asmenines ir grupines išlaidas laikantis nustatytų limitų.

Duomenys išsaugomi faile.

Išlaidų informacija ir vartotojų duomenys išsaugomi ir atnaujinami.

***Išvados:***

Visi pagrindiniai objektinio programavimo principai buvo pritaikyti.

Panaudoti dizaino šablonai tinka kodo plėtimui.

***Galimi patobulinimai:***

Sukurti grafinę vartotojo sąsają patogesniam naudojimui.

Generuoti mėnesines ataskaitas ar išlaidų grafikus.

Įdiegti vartotojo autentifikaciją ar prisijungimą prie paskyros slaptažodžiu.


